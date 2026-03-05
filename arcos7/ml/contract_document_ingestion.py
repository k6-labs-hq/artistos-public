from __future__ import annotations

from io import BytesIO


class ContractDocumentIngestion:
    """Extract plain text from contract documents for term extraction."""

    def extract_text(self, filename: str, content: bytes) -> dict:
        lower = (filename or "").lower()

        if lower.endswith((".txt", ".md")):
            return {
                "text": self._decode_text(content),
                "method": "plain_text_decode",
                "warnings": [],
            }

        if lower.endswith(".pdf"):
            return self._extract_pdf_text(content)

        if lower.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
            return self._extract_image_ocr(content)

        return {
            "text": "",
            "method": "unsupported",
            "warnings": [
                "Unsupported file type. Upload .txt, .md, .pdf, or image files (.png/.jpg/.tiff)."
            ],
        }

    @staticmethod
    def _decode_text(content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="ignore")

    def _extract_pdf_text(self, content: bytes) -> dict:
        warnings: list[str] = []
        text = ""
        method = "pdf_text_extraction"

        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(BytesIO(content))
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            text = "\n".join(parts).strip()
        except Exception:
            method = "pdf_text_unavailable"
            warnings.append(
                "Could not extract text from PDF (install pypdf for text PDFs)."
            )

        if not text:
            warnings.append(
                "No machine-readable PDF text was found. For scanned contracts, upload a text export "
                "or image and enable OCR dependencies (Pillow + pytesseract + tesseract binary)."
            )

        return {"text": text, "method": method, "warnings": warnings}

    def _extract_image_ocr(self, content: bytes) -> dict:
        warnings: list[str] = []
        method = "image_ocr"
        text = ""
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore

            img = Image.open(BytesIO(content))
            text = pytesseract.image_to_string(img).strip()
        except Exception:
            method = "image_ocr_unavailable"
            warnings.append(
                "OCR dependencies unavailable. Install Pillow + pytesseract and system tesseract."
            )

        return {"text": text, "method": method, "warnings": warnings}
