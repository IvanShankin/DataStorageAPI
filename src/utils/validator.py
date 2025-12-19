import base64

from fastapi import HTTPException


def decode_b64(value: str, expected_len: int, field: str) -> bytes:
    try:
        raw = base64.b64decode(value, validate=True)
    except Exception:
        raise HTTPException(400, f"{field} must be valid base64")

    if len(raw) != expected_len:
        raise HTTPException(400, f"{field} must be {expected_len} bytes")

    return raw
