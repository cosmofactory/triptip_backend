import pytest
from factory.alchemy import SQLAlchemyModelFactory

session = pytest.mark.usefixtures("session")

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session = session

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        async with cls._meta.sqlalchemy_session() as session:
            obj = model_class(*args, **kwargs)
            session.add(obj)
            await session.commit()
            return obj
