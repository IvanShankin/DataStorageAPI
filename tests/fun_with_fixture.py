from datetime import datetime

from src.config import ENC_VERSION
from src.service.data_base.core import get_db
from src.service.data_base.models import SecretsStrings, Secrets, SecretsFiles


async def create_secret_fab(
    name: str = "test_secret",
    is_deleted: bool = False,
    deleted_at: datetime = None,
) -> Secrets:
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
) -> SecretsStrings:
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


async def create_file_secret_fab(
    secret_id: int = None,
    version: int = 1,
    secret_name: str = "secret_string_test",
    file_stream: bytes = b"file_data",
    file_name: str = "test_file_name",
    nonce: bytes = b"123456789012",
    sha256: bytes = b"12345678901234567890123456789012",
) -> SecretsFiles:
    from src.config import SECRET_FILES_DIR
    SECRET_FILES_DIR.mkdir(exist_ok=True)

    with open(str(SECRET_FILES_DIR / file_name), "wb") as file:
        file.write(file_stream)

    if secret_id is None:
        secret = await create_secret_fab(name=secret_name)
        secret_id = secret.secret_id

    async with get_db() as session_db:
        secret_file = SecretsFiles(
            secret_id=secret_id,
            version=version,
            file_name=file_name,
            size_bytes=9,
            nonce=nonce,
            sha256=sha256
        )

        session_db.add(secret_file)
        await session_db.commit()
        await session_db.refresh(secret_file)

    return secret_file