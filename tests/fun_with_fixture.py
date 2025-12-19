from datetime import datetime, UTC

from src.config import ENC_VERSION
from src.service.data_base.core import get_db
from src.service.data_base.models import SecretsStrings, Secrets


async def create_secret_fab(
    name: str = "test_secret",
    is_deleted: bool = False,
    deleted_at: datetime = datetime.now(UTC),
):
    async with get_db() as session_db:
        secret = Secrets(
            name=name,
            is_deleted=is_deleted,
            deleted_at=deleted_at,
        )

        session_db.add(secret)
        await session_db.commit()
        await session_db.refresh(secret)

    return secret


async def create_string_secret_fab(
    secret_id: int = None,
    name: str = "secret_string_test",
    encrypted_data: bytes = b"encrypted_data",
    nonce: bytes = b"123456789012",
    sha256: bytes = b"12345678901234567890123456789012",
    version: int = 1,
):
    if secret_id is None:
        secret = await create_secret_fab(name=name)
        secret_id = secret.secret_id

    async with get_db() as session_db:
        secret_string = SecretsStrings(
            secret_id=secret_id,
            encrypted_data=encrypted_data,
            nonce=nonce,
            sha256=sha256,
            version=version,
            enc_version=ENC_VERSION,
        )

        session_db.add(secret_string)
        await session_db.commit()
        await session_db.refresh(secret_string)

    return secret_string