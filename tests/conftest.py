from http import HTTPStatus

import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.auth.auth import get_password_hash
from src.database.database import Base, get_db
from src.main import app
from src.users.dao import UserDAO

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:

        def override_get_db():
            return session

        app.dependency_overrides[get_db] = override_get_db
        yield session


@pytest.fixture(scope="session")
async def ac():
    """Create an AsyncClient instance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac(ac, session):
    """
    Create an authenticated AsyncClient instance.

    Add token to headers.
    Check cookies with tokens.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        password = get_password_hash("async_client_password1")
        user = await UserDAO.create(
            session,
            email="test@test.ru",
            username="LoggedInUser",
            password=password,
            bio="Some bio",
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
