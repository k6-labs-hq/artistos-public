from __future__ import annotations

import io
import mimetypes
import os
import socket
import struct
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class IngestedDocument:
    filename: str
    detected_type: str
    extension_type: str
    magic_type: str
    mime_type: str | None
    size_bytes: int
    validation_passed: bool = True
    pages: int = 1
    ocr_text: str | None = None
    extracted_rows: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class IngestionReport:
    virus_scan_passed: bool
    scanned_with: str
    documents: list[IngestedDocument]


class FileIngestionPipeline:
    """Generic multi-format ingestion pipeline for royalty statement uploads."""

    allowed_extensions = {".pdf", ".csv", ".xlsx", ".zip"}

    def virus_scan(self, content: bytes) -> tuple[bool, str]:
        # Try ClamAV first when configured; fallback to signature scan.
        if os.getenv("XR7_USE_CLAMAV", "1").strip() not in {"0", "false", "False"}:
            passed, scanner = self._clamav_scan(content)
            if scanner != "clamav_unavailable":
                return passed, scanner

        if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content:
            return False, "signature_scan:eicar"
        return True, "signature_scan:basic"

    def _clamav_scan(self, content: bytes) -> tuple[bool, str]:
        host = os.getenv("CLAMAV_HOST", "127.0.0.1")
        port = int(os.getenv("CLAMAV_PORT", "3310"))
        try:
            with socket.create_connection((host, port), timeout=2.0) as sock:
                sock.sendall(b"zINSTREAM\0")
                for i in range(0, len(content), 65536):
                    chunk = content[i:i + 65536]
                    sock.sendall(struct.pack(">I", len(chunk)))
                    sock.sendall(chunk)
                sock.sendall(struct.pack(">I", 0))
                resp = sock.recv(4096).decode("utf-8", errors="ignore")
                if "OK" in resp and "FOUND" not in resp:
                    return True, "clamav:ok"
                if "FOUND" in resp:
                    return False, f"clamav:found:{resp.strip()}"
                return False, f"clamav:unknown:{resp.strip()}"
        except Exception:  # noqa: BLE001
            return True, "clamav_unavailable"

    def _detect_magic_type(self, content: bytes) -> str:
        if content.startswith(b"%PDF-"):
            return "pdf"
        if content.startswith(b"PK"):
            if b"[Content_Types].xml" in content[:8192]:
                return "xlsx"
            return "zip"
        preview = content[:2048]
        if b"\x00" in preview:
            return "unknown"
        text = preview.decode("utf-8", errors="ignore")
        if "," in text and "\n" in text:
            return "csv"
        return "unknown"

    def detect_file_type(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix.lower()
        if ext in self.allowed_extensions:
            return ext.lstrip(".")
        guessed, _ = mimetypes.guess_type(filename)
        if guessed and "pdf" in guessed:
            return "pdf"
        if guessed and "csv" in guessed:
            return "csv"
        if guessed and "zip" in guessed:
            return "zip"
        if content.startswith(b"PK"):
            return "zip"
        return "unknown"

    def _validate_extension_magic(self, extension_type: str, magic_type: str) -> tuple[bool, str | None]:
        if extension_type == "unknown":
            return False, "File extension is not supported"
        if magic_type == "unknown":
            return False, "File signature could not be validated"
        if extension_type != magic_type:
            return False, f"Extension/magic mismatch: extension={extension_type}, magic={magic_type}"
        return True, None

    def split_pdf_pages(self, content: bytes) -> int:
        try:
            from pypdf import PdfReader  # type: ignore

            return max(1, len(PdfReader(io.BytesIO(content)).pages))
        except Exception:  # noqa: BLE001
            return 1

    def ocr_pdf_or_image(self, content: bytes) -> str | None:
        try:
            import pytesseract  # type: ignore
            from pdf2image import convert_from_bytes  # type: ignore

            pages = convert_from_bytes(content)
            text_parts: list[str] = []
            for page in pages:
                text_parts.append(pytesseract.image_to_string(page) or "")
            text = "\n".join(text_parts).strip()
            return text or None
        except Exception:  # noqa: BLE001
            return None

    def process_single(self, filename: str, content: bytes) -> IngestedDocument:
        detected = self.detect_file_type(filename, content)
        magic_type = self._detect_magic_type(content)
        ext = Path(filename).suffix.lower().lstrip(".") if Path(filename).suffix else "unknown"
        mime_type, _ = mimetypes.guess_type(filename)
        valid, validation_error = self._validate_extension_magic(ext, magic_type)
        doc = IngestedDocument(
            filename=filename,
            detected_type=detected,
            extension_type=ext,
            magic_type=magic_type,
            mime_type=mime_type,
            size_bytes=len(content),
            validation_passed=valid,
        )
        if validation_error:
            doc.warnings.append(validation_error)

        if detected == "pdf":
            doc.pages = self.split_pdf_pages(content)
            doc.ocr_text = self.ocr_pdf_or_image(content)
            if not doc.ocr_text:
                doc.warnings.append("OCR unavailable or produced no text")
        elif detected == "csv":
            doc.extracted_rows = [{"raw_preview": content.decode("utf-8", errors="ignore")[:2000]}]
        elif detected == "xlsx":
            try:
                wb = load_workbook(io.BytesIO(content), data_only=True, read_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    doc.warnings.append("XLSX file is empty")
                else:
                    headers = [str(h or "").strip() for h in rows[0]]
                    extracted: list[dict[str, Any]] = []
                    for row in rows[1:101]:
                        item: dict[str, Any] = {}
                        for i, h in enumerate(headers):
                            if not h:
                                continue
                            item[h] = row[i] if i < len(row) else None
                        if any(v not in (None, "") for v in item.values()):
                            extracted.append(item)
                    doc.extracted_rows = extracted
            except Exception as exc:  # noqa: BLE001
                doc.warnings.append(f"XLSX extraction failed: {exc}")
        elif detected == "zip":
            try:
                with zipfile.ZipFile(io.BytesIO(content), "r") as zf:
                    doc.extracted_rows = [{"bundle_member": name} for name in zf.namelist()]
            except zipfile.BadZipFile:
                doc.warnings.append("ZIP bundle is invalid")
        else:
            doc.warnings.append("Unsupported file type")

        return doc

    def process(self, uploads: list[tuple[str, bytes]], *, strict_validation: bool = True) -> IngestionReport:
        documents: list[IngestedDocument] = []
        overall_passed = True
        scanner_name = "signature_scan:basic"
        for filename, content in uploads:
            passed, scanner_name = self.virus_scan(content)
            overall_passed = overall_passed and passed
            doc = self.process_single(filename, content)
            if not passed:
                doc.warnings.append("Virus scan failed")
            if strict_validation and not doc.validation_passed:
                overall_passed = False
            documents.append(doc)

        return IngestionReport(
            virus_scan_passed=overall_passed,
            scanned_with=scanner_name,
            documents=documents,
        )
