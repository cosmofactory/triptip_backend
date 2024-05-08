from http import HTTPStatus

import asyncpg
import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from src.auth.auth import get_password_hash
from src.database.database import Base, engine
from src.main import app
from src.settings.config import settings
from src.users.dao import UserDAO


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Database setup.

    Database will be set up only in case of TEST environment.
    Database will we created before session test cases.
    """
    assert settings.MODE == "TEST"

    conn = await asyncpg.connect(
        user=settings.TEST_DB_USER,
        password=settings.TEST_DB_PASS,
        host=settings.TEST_DB_HOST,
        port=settings.TEST_DB_PORT,
    )

    try:
        await conn.execute(f"CREATE DATABASE {settings.TEST_DB_NAME}")
    except asyncpg.DuplicateDatabaseError:
        pass

    await conn.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def ac():
    """Create an AsyncClient instance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    """
    Create an authenticated AsyncClient instance.

    Add token to headers.
    Check cookies with tokens.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        password = get_password_hash("async_client_password1")
        await UserDAO.create(
            email="test@test.ru", username="LoggedInUser", password=password, bio="Some bio"
        )
        response = await ac.post(
            "/auth/login",
            data={"username": "test@test.ru", "password": "async_client_password1"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access_token = response.json()["access_token"]
        ac.headers.update({"Authorization": f"Bearer {access_token}"})
        assert response.status_code == HTTPStatus.OK
        assert ac.cookies.get("access_token") is not None
        assert ac.cookies.get("refresh_token") is not None
        yield ac
