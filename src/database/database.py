from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session

from src.settings.config import settings

DATABASE_URL = settings.DATABASE_URL
DATABASE_PARAMS = {}

engine = create_async_engine(DATABASE_URL, echo=True, **DATABASE_PARAMS)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[Session, None, None]:
    """Get local database connection."""
    async with SessionLocal() as session:
        yield session


# Dependency to use with ORM models
SessionDep = Annotated[Session, Depends(get_db)]


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for ORM models.

    AsyncAttrs is needed to use attributes of the model that are part of another model.
    If you get MissingGreenlet exception while working with ORM models, add this:
        trip.locations - MissingGreenlet exception
        trip.awaitable_attrs.locations - works fine
    Wanna know more?
    https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    """

    pass
