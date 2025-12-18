import base64

from pydantic import BaseModel, Field, field_validator


class CreateString(BaseModel):
    name: str = Field(..., max_length=255)
    encrypted_data: bytes
    nonce: bytes
    sha256: bytes


    @field_validator("encrypted_data", "nonce", "sha256", mode="before")
    @classmethod
    def decode_base64(cls, v):
        if isinstance(v, str):
            try:
                return base64.b64decode(v, validate=True)
            except Exception:
                raise ValueError("Must be valid base64 string")
        return v

    @field_validator("nonce")
    @classmethod
    def validate_nonce(cls, v: bytes) -> bytes:
        if len(v) != 12:
            raise ValueError("nonce must be exactly 12 bytes")
        return v

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, v: bytes) -> bytes:
        if len(v) != 32:
            raise ValueError("sha256 must be exactly 32 bytes")
        return v