import os
import uuid
from typing import Tuple

import aiofiles

from fastapi import UploadFile

from src.config import SECRET_FILES_DIR
from src.utils.core_logger import logger


def delete_file_safe(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.warning("file already deleted: %s", path)
    except Exception:
        logger.exception("failed to delete file: %s", path)


async def save_uploaded_file(upload: UploadFile) -> Tuple[str, int]:
    """
    :returns: Имя файла и размер в байтах
    """
    file_id = uuid.uuid4().hex
    size = 0

    SECRET_FILES_DIR.mkdir(exist_ok=True)
    path = SECRET_FILES_DIR / file_id

    async with aiofiles.open(path, "wb") as f:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            await f.write(chunk)

    return file_id, size
