from http import HTTPStatus

import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.auth.auth import get_password_hash
from src.database.database import Base, engine, get_db
from src.main import app
from src.settings.config import settings
from src.users.dao import UserDAO

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Database setup.

    Database will be set up only in case of TEST environment.
    Database will we created before session test cases.
    """
    assert settings.MODE == "TEST"
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


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
        async with override_get_db() as db:
            password = get_password_hash("async_client_password1")
            user = await UserDAO.create(
                db, email="test@test.ru", username="LoggedInUser", password=password, bio="Some bio"
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
            ac.user = user
            yield ac
