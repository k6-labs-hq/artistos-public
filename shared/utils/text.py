"""shared.utils.text – byte-stream / text parsing helpers.

Consolidates:
  - ``_decode_text`` in ``XR7/services/tvfilm_vertical.py``
  - ``_decode_text`` (static method) in ``XR7/ml/contract_document_ingestion.py``
"""

from __future__ import annotations

_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "utf-8", "latin-1")


def decode_bytes(raw: bytes, *, errors: str = "replace") -> str:
    """Decode *raw* bytes to ``str``, trying common encodings in order.

    Encodings tried: ``utf-8-sig`` (strips BOM), ``utf-8``, ``latin-1``.
    If all strict attempts fail the last encoding is used with *errors*
    handling (default ``"replace"``).

    Replaces ``_decode_text`` in ``tvfilm_vertical`` and the identically
    named static method in ``contract_document_ingestion``.
    """
    for encoding in _ENCODINGS[:-1]:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode(_ENCODINGS[-1], errors=errors)
