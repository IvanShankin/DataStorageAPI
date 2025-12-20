import base64
import io
import os

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.service.data_base.actions import get_secret_string, get_secret_files
from src.schemas.response import CreatedSecretStringData, CreatedSecretFileData

PAYLOAD_SECRET_STRING = {
    "name": "test_name",
    "encrypted_data": base64.b64encode(b"encrypted_data").decode(),
    "nonce": base64.b64encode(b"123456789012").decode(),  # ровно 12 байт
    "sha256": base64.b64encode(b"12345678901234567890123456789012").decode()  # ровно 32 байта
}

@pytest.mark.asyncio
async def test_create_string():
    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        response = await ac.post(
            "/secrets_strings/create_string",
            json=PAYLOAD_SECRET_STRING
        )

        assert response.status_code == 201

        response_data = CreatedSecretStringData(**(response.json()["data"]))
        assert await get_secret_string(response_data.name)


@pytest.mark.asyncio
async def test_create_string_new_version(create_string_secret):
    secret_name = "test_create_string"
    existing_secret = await create_string_secret(name=secret_name)

    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        new_payload = PAYLOAD_SECRET_STRING.copy()
        new_payload["name"] = secret_name

        response = await ac.post(
            "/secrets_strings/versions",
            json=new_payload
        )

        assert response.status_code == 201

        response_data = CreatedSecretStringData(**(response.json()["data"]))
        assert await get_secret_string(response_data.name, version=existing_secret.version + 1)


@pytest.mark.asyncio
async def test_create_file_with_version():
    from src.config import SECRET_FILES_DIR
    name = "test_file_secret"
    file_content_1 = io.BytesIO(b"encrypted_file_content_1")

    nonce = base64.b64encode(b"123456789012").decode()
    sha256 = base64.b64encode(b"12345678901234567890123456789012").decode()

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as ac:
        # 2 версия
        response = await ac.post(
            "/secrets_files/create_files",
            files={"file": ("file1.bin", file_content_1, "application/octet-stream")},
            data={"name": name, "nonce": nonce, "sha256": sha256},
        )
        assert response.status_code == 201
        secret_file = await get_secret_files(name)
        assert secret_file is not None

        assert os.path.isfile(SECRET_FILES_DIR / secret_file.file_name)


@pytest.mark.asyncio
async def test_create_string_new_version(create_file_secret_fix):
    name = "test_file_secret"
    secret_file = await create_file_secret_fix(secret_name=name)

    file_content_1 = io.BytesIO(b"encrypted_file_content_1")

    nonce = base64.b64encode(b"123456789012").decode()
    sha256 = base64.b64encode(b"12345678901234567890123456789012").decode()

    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        # 2 версия
        response = await ac.post(
            "/secrets_files/versions",
            files={"file": ("file1.bin", file_content_1, "application/octet-stream")},
            data={"name": name, "nonce": nonce, "sha256": sha256},
        )

        assert response.status_code == 201

        assert await get_secret_files(name, version=2)


