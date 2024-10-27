from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.user_factories import UserFactory


async def test_smoke_not_coming(ac: AsyncClient):
    response = await ac.get("/about_project")
    print(response.json())
    assert response.status_code == HTTPStatus.OK
    assert "Error" not in response.json().keys()


class TestUsers:
    async def test_users_list(self, ac: AsyncClient, session: AsyncSession):
        """
        Test users appear on /users endpoint.

        Create 10 users and check if they appear on /users endpoint.
        """
        check_users = []
        for _ in range(10):
            user = await UserFactory.create(db=session)
            check_users.append(user)
        response = await ac.get("/users")
        assert response.status_code == HTTPStatus.OK
        for user in check_users:
            assert any(response_user["email"] == user.email for response_user in response.json())

    async def test_user_profile_for_me(self, authenticated_ac: AsyncClient):
        """
        Test user profile endpoint.

        When accessing this endpoint for your own user id,
         you should see your own profile with more data.
        """

        response = await authenticated_ac.get(f"/users/profile/{authenticated_ac.user.id}")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["email"] == authenticated_ac.user.email

    async def test_user_profile_for_other_user(
        self, authenticated_ac: AsyncClient, session: AsyncSession
    ):
        """
         Test user profile endpoint.

        When accessing this endpoint for another user id,
          you should see their profile with less data.
        """
        user = await UserFactory.create(db=session)
        response = await authenticated_ac.get(f"/users/profile/{user.id}")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["email"] != authenticated_ac.user.email
