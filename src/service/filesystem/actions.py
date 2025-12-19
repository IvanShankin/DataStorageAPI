import os

from src.utils.core_logger import logger


def delete_file_safe(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.warning("file already deleted: %s", path)
    except Exception:
        logger.exception("failed to delete file: %s", path)

