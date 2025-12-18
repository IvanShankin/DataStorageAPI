import requests
import pytest

from src.config import BASE_DIR
from tests.conftest import uvicorn_server


async def test_certificate(uvicorn_server):
    cert = (
        str(BASE_DIR / "certs" / "server_shop_cert.pem"),
        str(BASE_DIR / "certs" / "server_shop_key.pem")
    )
    ca = str(BASE_DIR / "certs" / "ca.crt")

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


async def test_fail_ssl(uvicorn_server):
    with pytest.raises(requests.exceptions.SSLError):
        r = requests.get(
            "https://127.0.0.1:7591/health",
            timeout=10,
        )
