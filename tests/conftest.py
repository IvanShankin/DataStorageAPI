import os
import signal
import socket
import subprocess
import sys
import time

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from src.service.data_base import core

load_dotenv()    # Загружает переменные из .env
MODE = os.getenv('MODE')
SSL_CLIENT_CERT_FILE = os.getenv('SSL_CLIENT_CERT_FILE')
SSL_CLIENT_KEY_FILE = os.getenv('SSL_CLIENT_KEY_FILE')

from src.config import SSL_CERT_FILE, SSL_KEY_FILE, SSL_CA_FILE
from src.service.data_base.filling_database import create_database

import pytest

from tests.helpers_fixture import *

@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_database_fixture():
    if MODE != "TEST":
        raise Exception("Используется основная БД!")

    await create_database()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def replacement_needed_modules(replace_secret_files_dir):
    pass


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(monkeypatch):
    # создаём новый engine для теста
    test_engine = create_async_engine(core.SQL_DB_URL, future=True)

    # подменяем глобальный engine и sessionmaker внутри core.py
    monkeypatch.setattr(core, "engine", test_engine)
    core.session_local.configure(bind=test_engine)

    # дропаем и создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(core.Base.metadata.drop_all)
        await conn.run_sync(core.Base.metadata.create_all)

    yield

    await test_engine.dispose()

def wait_for_port(host: str, port: int, timeout: float = 5.0):
    """Ждём, пока сервер реально начнёт слушать порт"""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return
            except OSError:
                time.sleep(0.1)
    raise RuntimeError("Uvicorn did not start in time")


@pytest.fixture(scope="session")
def uvicorn_server():
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--host", "127.0.0.1",
        "--port", "7591",
        "--ssl-certfile", str(SSL_CERT_FILE),
        "--ssl-keyfile", str(SSL_KEY_FILE),
        "--ssl-ca-certs", str(SSL_CA_FILE),
        "--ssl-cert-reqs", "2",  # ssl.CERT_REQUIRED
        "--log-level", "warning",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        wait_for_port("127.0.0.1", 7591)
        yield
    finally:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
