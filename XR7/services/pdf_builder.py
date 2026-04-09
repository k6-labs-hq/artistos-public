from __future__ import annotations

import io


def safe_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(lines: list[str]) -> bytes:
    page_lines = lines[:46]
    content_ops = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    for line in page_lines:
        content_ops.append(f"({safe_pdf_text(line)}) Tj")
        content_ops.append("T*")
    content_ops.append("ET")
    content = "\n".join(content_ops).encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(
        f"5 0 obj << /Length {len(content)} >> stream\n".encode("utf-8")
        + content
        + b"\nendstream endobj\n"
    )

    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref_start = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    output.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        output.write(f"{off:010d} 00000 n \n".encode("utf-8"))
    output.write(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("utf-8")
    )
    return output.getvalue()
