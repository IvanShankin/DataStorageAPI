import requests
import pytest
from httpx import AsyncClient, ASGITransport

from src.config import BASE_DIR
from src.main import app
from tests.conftest import uvicorn_server



@pytest.mark.asyncio
async def test_certificate(uvicorn_server):
    cert = (
        str(BASE_DIR / "certs" / "storage" / "server_shop_cert.pem"),
        str(BASE_DIR / "certs" / "storage" / "server_shop_key.pem")
    )
    ca = str(BASE_DIR / "certs" / "ca" / "ca.crt")

    r = requests.get(
        "https://127.0.0.1:7591/health",
        cert=cert,
        verify=ca,
        timeout=10,
        proxies={
            "http": None,
            "https": None,
        },
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_fail_ssl(uvicorn_server):
    with pytest.raises(requests.exceptions.SSLError):
        r = requests.get(
            "https://127.0.0.1:7591/health",
            timeout=10,
        )


@pytest.mark.asyncio
async def test_get_secret_string(create_string_secret):
    secret_name = "test_create_string"
    existing_secret = await create_string_secret(name=secret_name)

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as ac:
        # Первая версия
        response = await ac.get(
            f"/secret_string/{secret_name}",
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_secret_file_meta(create_file_secret_fix):
    name = "test_file"
    await create_file_secret_fix(secret_name=name)

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(f"/secrets/files/{name}")
        assert response.status_code == 200
        assert response.json()["name"] == name



@pytest.mark.asyncio
async def test_download_secret_file(create_file_secret_fix):
    name = "test_file_download"


    payload = b"encrypted_file_content"
    created_file = await create_file_secret_fix(
        secret_name=name,
        file_content=payload,
    )

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(f"/secrets/files/{name}/download")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"

        content = response.content
        assert content == payload