import base64

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.server_exceptions import NameAlreadyExists
from src.service.data_base.core import get_db
from src.service.data_base.models import SecretsStrings, SecretsFiles


# async def get_max_version_in_secret_string(session_db: AsyncSession, name: str) -> int:
#     result_db = await session_db.execute(select(SecretsFiles.version).where(SecretsFiles.name == name))
#     return result_db.scalar_one_or_none()
#
#
# async def get_max_version_in_secret_file(session_db: AsyncSession, name: str) -> int:
#     result_db = await session_db.execute(select(SecretsFiles.version).where(SecretsFiles.name == name))
#     return result_db.scalar_one_or_none()


async def get_secret_string(name: str) -> SecretsStrings:
    async with get_db() as session_db:
        async with session_db.begin(): # в транзакции
            result_db = await session_db.execute(select(SecretsStrings).where(SecretsStrings.name == name))
            return result_db.scalar_one_or_none()


async def get_secret_files(name: str) -> SecretsFiles:
    async with get_db() as session_db:
        result_db = await session_db.execute(select(SecretsFiles).where(SecretsFiles.name == name))
        return result_db.scalar_one_or_none()


async def create_secret_string(name: str, encrypted_data: bytes, nonce: bytes, sha256: bytes) -> SecretsStrings:
    if await get_secret_string(name):
        raise NameAlreadyExists(name)

    async with get_db() as session_db:
        secret_string = SecretsStrings(
            name=name,
            encrypted_data=encrypted_data,
            nonce=nonce,
            sha256=sha256
        )

        session_db.add(secret_string)
        await session_db.commit()
        await session_db.refresh(secret_string)

    return secret_string