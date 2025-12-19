from datetime import datetime, UTC
from typing import Callable, Awaitable, List

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload

from src.config import ENC_VERSION, MEDIA_DIR, SECRET_FILES_DIR
from src.exceptions.server_exceptions import NameAlreadyExists, SecretNotFound
from src.schemas.requests import SecretStringCreate
from src.service.data_base.core import get_db
from src.service.data_base.models import SecretsStrings, SecretsFiles, Secrets
from src.service.filesystem.actions import save_uploaded_file
from src.utils.core_logger import logger
from src.utils.validator import decode_b64


async def _get_last_version_secret(db_table: object, name: str) -> int | None:
    """
    :param db_table: Таблица должна иметь поле "name" и "version", быть связана с таблице Secrets
    :param name: Искомое имя
    """
    async with get_db() as session_db:
        result = await session_db.execute(
            select(db_table.version)
            .join(Secrets)
            .where(
                (Secrets.name == name) &
                (Secrets.is_deleted == False)
            )
            .order_by(db_table.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _get_secret(
    db_table: object,
    func_get_last_version: Callable[[str], Awaitable[int]],
    name: str,
    version: int = None,
) -> object:
    """
    :param db_table: Таблица должна иметь поле "name" и "version", быть связана с таблице Secrets
    :param func_get_last_version: Должна принимать имя и возвращать версию
    :param name: Искомое имя
    :param version: При указании версии вернёт по ней. Если не указывать, то вернёт последнюю
    """
    if version is None:
        version = await func_get_last_version(name)
        if version is None:
            return None

    async with get_db() as session_db:
        result_db = await session_db.execute(
            select(db_table)
            .join(Secrets)
            .where(
                (Secrets.name == name) &
                (db_table.version == version) &
                (Secrets.is_deleted == False)
            )
        )
        return result_db.scalar_one_or_none()


async def get_last_version_in_secret_string(name: str) -> int:
    result = await _get_last_version_secret(SecretsStrings, name)
    return result if result else 0


async def get_last_version_in_secret_file(name: str) -> int:
    result = await _get_last_version_secret(SecretsFiles, name)
    return result if result else 0


async def get_secret_string(name: str, version: int = None) -> SecretsStrings | None:
    """
    При указании версии вернёт по ней. Если не указывать, то вернёт последнюю
    """
    return await _get_secret(SecretsStrings, get_last_version_in_secret_string, name, version)


async def get_secret_files(name: str, version: int = None) -> SecretsFiles | None:
    """
    При указании версии вернёт по ней. Если не указывать, то вернёт последнюю
    """
    return await _get_secret(SecretsFiles, get_last_version_in_secret_file, name, version)


async def get_secret(name: str) -> Secrets | None:
    """
    Вернёт даже удалённый секрет (Secrets.is_delete == True)
    :return Secrets: Вернёт со всеми погруженными связями
    """
    async with get_db() as session_db:
        result_db = await session_db.execute(
            select(Secrets)
            .options(selectinload(Secrets.secret_string), selectinload(Secrets.secret_file))
            .where(Secrets.name == name)
        )
        return result_db.scalar_one_or_none()


async def create_secret_string(
    name: str,
    encrypted_data: bytes,
    nonce: bytes,
    sha256: bytes,
    version: int = 1,
    new_secret: bool = True,
    secret_id: int = None
) -> SecretsStrings:
    """
    :param new_secret: Если установить True, то будет проверка на наличие такой строки, если есть, то вызовет исключение NameAlreadyExists
    :param secret_id: Если не указать, то будет создана новая запись в таблице Secrets. Необходим только для новой версии
    :except NameAlreadyExists: Если данное имя занято (только при создании нового секрета)
    """
    if (not new_secret and not secret_id) or (new_secret and secret_id):
        raise ValueError()

    async with get_db() as session_db:
        if new_secret:
            if await get_secret_string(name):
                raise NameAlreadyExists(name)

            secret = Secrets(name=name)
            session_db.add(secret)

            await session_db.flush()

            secret_id = secret.secret_id

        secret_string = SecretsStrings(
            secret_id=secret_id,
            encrypted_data=encrypted_data,
            nonce=nonce,
            sha256=sha256,
            version=version,
            enc_version=ENC_VERSION
        )

        session_db.add(secret_string)
        await session_db.commit()
        await session_db.refresh(secret_string)

    return secret_string


async def create_secret_file_service(
    name: str,
    file: UploadFile,
    nonce_b64: str,
    sha256_b64: str,
):
    nonce = decode_b64(nonce_b64, 12, "nonce")
    sha256 = decode_b64(sha256_b64, 32, "sha256")

    async with get_db() as session_db:
        secret = await get_secret(name)

        async with session_db.begin():
            if secret and secret.is_deleted:
                raise HTTPException(409, "Secret is deleted")

            if secret:
                raise NameAlreadyExists(name)

            version = await get_last_version_in_secret_file(name) + 1

            file_name = await save_uploaded_file(file)

            secret = Secrets(name=name)
            session_db.add(secret)

            await session_db.flush()

            db_file = SecretsFiles(
                secret_id=secret.secret_id,
                version=version,
                file_name=file_name,
                size_bytes=file.spool_max_size if hasattr(file, "spool_max_size") else 0,
                nonce=nonce,
                sha256=sha256,
            )

            session_db.add(db_file)

        return db_file


async def create_next_string_version(data: SecretStringCreate) -> SecretsStrings:
    last_version = await get_last_version_in_secret_string(data.name)
    secret = await get_secret_string(data.name)

    if not last_version or not secret:
        raise SecretNotFound(data.name)

    return await create_secret_string(
        version=last_version + 1,
        new_secret=False,
        secret_id=secret.secret_id,
        **(data.model_dump())
    )


async def mark_is_delete_secret(name: str) -> bool:
    async with get_db() as session_db:
        async with session_db.begin():
            result_db = await session_db.execute(
                select(Secrets)
                .where(Secrets.name == name)
                .with_for_update()
            )
            secret = result_db.scalar_one_or_none()

            if not secret:
                logger.info("attempt to mark remote a secret that does not exist")
                return False

            if secret.is_deleted:
                logger.info("attempt to mark remote a secret that has already been matk Remote")
                return True

            secret.is_deleted = True
            secret.deleted_at = datetime.now(UTC)
            return True


async def purge_secret_db(name: str) -> List[str]:
    """
    Возвращает список путей файлов, которые нужно удалить
    """
    path_for_removal = []
    async with get_db() as session_db:
        async with session_db.begin():
            result_db = await session_db.execute(
                select(Secrets)
                .options(selectinload(Secrets.secret_string), selectinload(Secrets.secret_file))
                .where(Secrets.name == name)
            )
            secret: Secrets = result_db.scalar_one_or_none()

            if not secret:
                logger.info("attempt to delete a secret that does not exist")
                return path_for_removal

            if secret.secret_string:
                await session_db.execute(
                    delete(SecretsStrings)
                    .where(SecretsStrings.secret_id == secret.secret_id)
                )
            else:
                result_db = await session_db.execute(
                    delete(SecretsFiles)
                    .where(SecretsFiles.secret_id == secret.secret_id)
                    .returning(SecretsFiles)
                )
                deleted_secrets: List[SecretsFiles] = result_db.scalars().all()

                path_for_removal = [SECRET_FILES_DIR / secret_file.file_name for secret_file in deleted_secrets]


            await session_db.execute(
                delete(Secrets)
                .where(Secrets.secret_id == secret.secret_id)
            )


    return path_for_removal

