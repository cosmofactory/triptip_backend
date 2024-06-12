from http import HTTPStatus
import asyncio
import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
import pytest_asyncio
from src.auth.auth import get_password_hash
from src.database.database import Base, engine, get_db
from src.main import app
from src.settings.config import settings
from src.users.dao import UserDAO

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(event_loop):
    assert settings.MODE == "TEST"
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    engine.sync_engine.dispose()


@pytest.fixture(scope="session")
async def session(engine):
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with engine.connect() as conn:
        tsx = await conn.begin()
        async with SessionLocal(bind=conn) as session:
            nested_tsx = await conn.begin_nested()
            yield session

            if nested_tsx.is_active:
                await nested_tsx.rollback()
            await tsx.rollback()


app.dependency_overrides[get_db] = session


@pytest.fixture(scope="session")
async def ac():
    """Create an AsyncClient instance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac(session):
    """
    Create an authenticated AsyncClient instance.

    Add token to headers.
    Check cookies with tokens.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        password = get_password_hash("async_client_password1")
        user = await UserDAO.create(
            session, email="test@test.ru", username="LoggedInUser", password=password, bio="Some bio"
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
