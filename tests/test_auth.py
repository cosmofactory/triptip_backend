import asyncio
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.auth.auth import get_password_hash
from src.users.dao import UserDAO


class TestAuth:
    @pytest.mark.parametrize(
        "email, username, status",
        [
            ("test@test.com", "TestUser", HTTPStatus.CREATED),
            ("test@test.com", "TestUser", HTTPStatus.CONFLICT),
            ("X", "TestUser1", HTTPStatus.UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_user_registration(self, ac: AsyncClient, email, username, status):
        """
        Test user registration.

        1. Register a user and check if it appears in the database.
        2. Check that user with the same email cannot be registered.
        3. Check that invalid email returns 422.
        """
        user_data = {"email": email, "username": username, "password": "qwerty1", "bio": "Some bio"}

        response = await ac.post(
            "/auth/register",
            json=user_data,
        )
        assert response.status_code == status
        if response.status_code == HTTPStatus.CREATED:
            check_user = await UserDAO.get_one_or_none(email=user_data["email"])
            assert check_user.email == user_data["email"]

    async def test_user_login(self, ac: AsyncClient):
        """
        Test user login.

        1. Register a user.
        2. Login with the registered user.
        3. Check that the response contains an access token.
        """
        password = get_password_hash("login_password4")
        await UserDAO.create(
            email="user_login_test@test.ru",
            username="UserLoginTest",
            password=password,
            bio="Some bio",
        )
        response = await ac.post(
            "/auth/login",
            data={"username": "user_login_test@test.ru", "password": "login_password4"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.json().keys()
        assert "refresh_token" in response.json().keys()

    async def test_token_refresh(self, authenticated_ac: AsyncClient):
        """
        Test token refresh.

        1. Get old tokens from cookies.
        2. Refresh tokens.
        3. Check that new tokens are different from the old ones in both response and cookies.
        """
        old_access_token = authenticated_ac.cookies.get("access_token")
        old_refresh_token = authenticated_ac.cookies.get("refresh_token")
        await asyncio.sleep(1)  # giving time to refresh token
        response = await authenticated_ac.post("auth/refresh")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["access_token"] != old_access_token
        assert response.json()["refresh_token"] != old_refresh_token
        assert authenticated_ac.cookies.get("access_token") != old_access_token
        assert authenticated_ac.cookies.get("refresh_token") != old_refresh_token
