import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from src.main import app
from src.service.data_base.actions import get_secret_string, get_secret
from src.service.data_base.core import get_db
from src.service.data_base.models import Secrets


@pytest.mark.asyncio
async def test_mark_delete(create_string_secret):
    secret_name = "test_create_string"
    await create_string_secret(name=secret_name)

    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        response = await ac.delete(
            f"/secrets/{secret_name}",
        )

        assert not await get_secret_string(secret_name)


@pytest.mark.asyncio
async def test_purge_secret(create_string_secret):
    secret_name = "test_create_string"
    await create_string_secret(name=secret_name)

    async with AsyncClient(
            transport=ASGITransport(app),
            base_url="http://test",
    ) as ac:
        response = await ac.post(
            f"/secrets/{secret_name}/purge",
        )

        assert not await get_secret(secret_name)



# сделать тест на удаление файла
# сделать тест на удаление файла
# сделать тест на удаление файла