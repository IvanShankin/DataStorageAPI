import base64

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.service.data_base.actions import get_secret_string
from src.schemas.response import CreatedSecretStringData


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