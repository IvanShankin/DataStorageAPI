import pytest_asyncio

from fun_with_fixture import create_string_secret_fab, create_secret_fab



@pytest_asyncio.fixture
async def create_secret():
    return create_secret_fab


@pytest_asyncio.fixture
async def create_string_secret():
    return create_string_secret_fab

