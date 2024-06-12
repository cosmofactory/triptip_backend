from factory.alchemy import SQLAlchemyModelFactory

from tests.conftest import session

# session = scoped_session(async_session_maker)


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session = session

    # @classmethod
    # async def _create(cls, model_class, *args, **kwargs):
    #     async with TestingSessionLocal() as session:
    #         obj = model_class(*args, **kwargs)
    #         session.add(obj)
    #         await session.commit()
    #         return obj
