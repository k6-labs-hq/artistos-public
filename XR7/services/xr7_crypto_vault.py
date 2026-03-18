from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets


class VaultError(RuntimeError):
    pass


def _master_key() -> bytes:
    raw = (os.environ.get("XR7_VAULT_MASTER_KEY") or "xr7-dev-vault-key-change-me").encode("utf-8")
    return hashlib.sha256(raw).digest()


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def seal(plaintext: str) -> str:
    pt = plaintext.encode("utf-8")
    key = _master_key()
    nonce = secrets.token_bytes(16)
    stream = _keystream(key, nonce, len(pt))
    cipher = bytes(a ^ b for a, b in zip(pt, stream, strict=True))
    tag = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
    packed = nonce + cipher + tag
    return base64.urlsafe_b64encode(packed).decode("ascii")


def open_sealed(sealed_value: str) -> str:
    try:
        packed = base64.urlsafe_b64decode(sealed_value.encode("ascii"))
    except Exception as exc:  # noqa: BLE001
        raise VaultError("sealed payload is not valid base64") from exc

    if len(packed) < 48:
        raise VaultError("sealed payload is too short")

    nonce = packed[:16]
    tag = packed[-32:]
    cipher = packed[16:-32]

    key = _master_key()
    expected = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise VaultError("sealed payload integrity check failed")

    stream = _keystream(key, nonce, len(cipher))
    pt = bytes(a ^ b for a, b in zip(cipher, stream, strict=True))
    return pt.decode("utf-8")
