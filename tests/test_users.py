from http import HTTPStatus

import pytest
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

    @pytest.mark.parametrize(
        "user_id, status",
        [
            (None, HTTPStatus.OK),
            (999, HTTPStatus.NOT_FOUND),
            ("X", HTTPStatus.UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_user_detail(
        self, ac: AsyncClient, session: AsyncSession, user_id: int | str, status
    ):
        """
        Test user detail endpoint.

        Create a user and check if it appears on /users/get_user/{user_id} endpoint.
        Check that nonexistent user returns 404.
        Check that invalid user_id returns 422.
        """
        user = await UserFactory.create(db=session)
        response = await ac.get(f"/users/get_user/{user_id if user_id else user.id}")
        assert response.status_code == status
        if not user_id:
            assert response.json()["email"] == user.email
            assert response.json()["username"] == user.username

    async def test_user_me(self, authenticated_ac: AsyncClient):
        """
        Test user detail endpoint.

        Create a user and check if it appears on /users/me endpoint.
        """
        response = await authenticated_ac.get("/users/me")
        print(response.json())
        assert response.status_code == HTTPStatus.OK
        assert response.json()["email"] is not None
