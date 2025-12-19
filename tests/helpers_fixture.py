import os
import shutil

import pytest_asyncio

from tests.fun_with_fixture import create_string_secret_fab, create_secret_fab, create_file_secret_fab


@pytest_asyncio.fixture
async def create_secret():
    return create_secret_fab


@pytest_asyncio.fixture
async def create_string_secret():
    return create_string_secret_fab


@pytest_asyncio.fixture
async def create_file_secret_fix():
    return create_file_secret_fab


@pytest_asyncio.fixture
async def replace_secret_files_dir(monkeypatch, tmp_path):
    from src import config
    from src.service.filesystem import actions as actions_files
    from src.service.data_base import actions as actions_ser
    from src.routers import get

    new_secret_files_dir = tmp_path / "secret_files_test"
    monkeypatch.setattr(config, "SECRET_FILES_DIR", new_secret_files_dir)
    monkeypatch.setattr(actions_files, "SECRET_FILES_DIR", new_secret_files_dir)
    monkeypatch.setattr(actions_ser, "SECRET_FILES_DIR", new_secret_files_dir)
    monkeypatch.setattr(actions_ser, "SECRET_FILES_DIR", new_secret_files_dir)
    monkeypatch.setattr(get, "SECRET_FILES_DIR", new_secret_files_dir)

    yield

    if os.path.isdir(new_secret_files_dir):
        shutil.rmtree(new_secret_files_dir)  # удаляет директорию созданную для тестов