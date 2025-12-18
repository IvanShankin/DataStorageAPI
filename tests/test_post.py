import base64

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.service.data_base.actions import get_secret_string
from src.schemas.response import CreatedSecretStringData


@pytest.mark.asyncio
async def test_create_string():
    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        payload = {
            "name": "test_name",
            "encrypted_data": base64.b64encode(b"encrypted_data").decode(),
            "nonce": base64.b64encode(b"123456789012").decode(),  # ровно 12 байт
            "sha256": base64.b64encode(b"12345678901234567890123456789012").decode()  # ровно 32 байта
        }
        response = await ac.post(
            "/create_string",
            json=payload
        )

        assert response.status_code == 201
        response_data = CreatedSecretStringData(**(response.json()["data"]))

        assert await get_secret_string(response_data.name)
