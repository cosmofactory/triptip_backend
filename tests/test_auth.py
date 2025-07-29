import asyncio
import datetime
from http import HTTPStatus

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import (
    create_action_token,
    get_password_hash,
    verify_password,
)
from src.settings.config import settings
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
    async def test_user_registration(
        self, ac: AsyncClient, session: AsyncSession, email, username, status
    ):
        """
        Test user registration.

        1. Register a user and check if it appears in the database.
        2. Check that user with the same email cannot be registered.
        3. Check that invalid email returns 422.
        """
        user_data = {
            "email": email,
            "username": username,
            "password": "qwerty1",
            "bio": "Some bio",
            "first_name": "Test",
            "last_name": "User",
        }

        response = await ac.post(
            "/auth/register",
            json=user_data,
        )
        assert response.status_code == status
        if response.status_code == HTTPStatus.CREATED:
            check_user = await UserDAO.get_one_or_none(session, email=user_data["email"])
            assert check_user.email == user_data["email"]

    async def test_user_login(self, ac: AsyncClient, session: AsyncSession):
        """
        Test user login.

        1. Register a user.
        2. Login with the registered user.
        3. Check that the response contains an access token.
        """
        password = get_password_hash("login_password4")
        await UserDAO.create(
            session,
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

    async def test_verify_email_handler(self, ac: AsyncClient, session: AsyncSession):
        """
        Test email verification handler.

        1. Create a new user (initially unverified).
        2. Generate an email verification token for that user.
        3. Call /auth/verify with the token.
        4. Ensure a 200 OK, that access & refresh tokens are returned,
           and that the user is marked as verified in the database.
        """
        email = "verify_test@example.com"
        raw_password = "VerifyPass123"
        hashed = get_password_hash(raw_password)
        await UserDAO.create(
            session,
            email=email,
            username="VerifyUser",
            password=hashed,
            bio="Oh yes",
        )

        user_before = await UserDAO.get_one_or_none(session, email=email)
        assert user_before is not None
        assert user_before.is_verified is False

        token = create_action_token(email, "verify", datetime.timedelta(hours=1))

        response = await ac.post(
            "/auth/verify",
            json={"token": token},
        )
        assert response.status_code == HTTPStatus.OK

        payload = response.json()
        assert "access_token" in payload
        assert "refresh_token" in payload

        user_after = await UserDAO.get_one_or_none(session, email=email)
        assert user_after is not None
        assert user_after.is_verified is True

    @pytest.mark.parametrize(
        "email, expires_delta",
        [
            ("test@example.com", datetime.timedelta(hours=1)),
            ("user@domain.com", datetime.timedelta(hours=2)),
            ("another@example.com", datetime.timedelta(hours=3)),
        ],
    )
    def test_create_email_verification_token(self, email, expires_delta):
        token = create_action_token(email, "verify", expires_delta)
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload.get("sub") == email
        assert payload.get("verify") is True

        now = datetime.datetime.now(datetime.timezone.utc)
        token_exp = datetime.datetime.fromtimestamp(payload.get("exp"), tz=datetime.timezone.utc)

        expected_exp = now + expires_delta
        time_difference = abs((token_exp - expected_exp).total_seconds())
        assert time_difference < 2, f"Expiration delta {time_difference} exceeded allowed tolerance"

    async def test_resend_verification_email_not_verified(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
        mock_email_service,
    ):
        """
        Test successful resending verification email.

        1. Make an unverified user.
        2. Call /auth/resend_verification.
        3. Ensure a 202_ACCEPTED with success message and expiration time.
        """
        current_user = authenticated_ac.user
        assert current_user is not None

        await UserDAO.update(session, current_user.id, is_verified=False)
        assert current_user.is_verified is False

        response = await authenticated_ac.post("/auth/resend_verification")

        assert response.status_code == HTTPStatus.ACCEPTED

        response_data = response.json()
        assert response_data["message"] == "Verification email sent successfully"
        assert "email" in response_data
        assert response_data["email"] == current_user.email
        assert "expires_in_hours" in response_data

    async def test_resend_verification_email_already_verified(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
        mock_email_service,
    ):
        """
        Resend verification email for verified user.

        1. Verify the user.
        2. Call /auth/resend_verification.
        3. Ensure a 400_BAD_REQUEST with an error message.
        """
        current_user = authenticated_ac.user
        assert current_user is not None

        await UserDAO.update(session, current_user.id, is_verified=True)
        assert current_user.is_verified is True

        response = await authenticated_ac.post("/auth/resend_verification")
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "already verified" in response.json()["detail"]

    async def test_resend_verification_email_unauthenticated(
        self,
        ac: AsyncClient,
        mock_email_service,
    ):
        """
        Resend verification email without authentication.

        1. Call /auth/resend_verification without authentication.
        2. Ensure a 401_UNAUTHORIZED with an error message.
        """
        response = await ac.post("/auth/resend_verification")

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "detail" in response.json()

    @pytest.mark.parametrize(
        "email, expires_delta",
        [
            ("test@example.com", datetime.timedelta(hours=1)),
            ("user@domain.com", datetime.timedelta(hours=2)),
            ("another@example.com", datetime.timedelta(hours=3)),
        ],
    )
    def test_create_reset_token(self, email, expires_delta):
        token = create_action_token(email, "reset", expires_delta)
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload.get("sub") == email
        assert payload.get("reset") is True

        now = datetime.datetime.now(datetime.timezone.utc)
        token_exp = datetime.datetime.fromtimestamp(payload.get("exp"), tz=datetime.timezone.utc)

        expected_exp = now + expires_delta
        time_difference = abs((token_exp - expected_exp).total_seconds())
        assert time_difference < 2, f"Expiration delta {time_difference} exceeded allowed tolerance"

    async def test_request_password_recovery_handler(
        self,
        ac: AsyncClient,
        session: AsyncSession,
        mock_email_service,
    ):
        """
        Test password recovery request endpoint.

        1. Create a user.
        2. Request password recovery for existing user
        3. Ensure 200_OK with success message.
        """
        email = "recovery_test@example.com"
        raw_password = "RecoveryPass123"
        hashed = get_password_hash(raw_password)
        await UserDAO.create(
            session,
            email=email,
            username="RecoveryUser",
            password=hashed,
            bio="RequestBio",
        )

        user = await UserDAO.get_one_or_none(session, email=email)
        assert user is not None

        response = await ac.post(
            "/auth/request_password_recovery",
            json={"email": email},
        )

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["message"] == "Password recovery email sent successfully"
        assert response_data["email"] == user.email
        assert "expires_in_hours" in response_data

    async def test_request_password_recovery_handler_non_existing_user(
        self,
        ac: AsyncClient,
        mock_email_service,
    ):
        """
        Test password recovery request for non-existing user.

        Expecting 200_OK response with a success message.
        No reset token should be generated or sent.
        """
        non_existent_email = "nonexistent@example.com"
        response = await ac.post(
            "/auth/request_password_recovery",
            json={"email": non_existent_email},
        )
        assert response.status_code == HTTPStatus.OK

        response_data = response.json()

        assert response_data["message"] == "Password recovery email sent successfully"
        assert response_data["email"] == non_existent_email
        assert "expires_in_hours" in response_data

    async def test_reset_password_handler(
        self,
        ac: AsyncClient,
        session: AsyncSession,
    ):
        """
        Test password reset endpoint.

        1. Create a user.
        2. Generate a valid reset token for the user.
        3. Reset password with valid token.
        4. Ensure 200_OK with success message
        """
        email = "reset_test@example.com"
        old_raw_password = "OldPassTest123"
        new_raw_password = "NewPassTest456"
        hashed = get_password_hash(old_raw_password)
        await UserDAO.create(
            session,
            email=email,
            username="ResetUser",
            password=hashed,
            bio="ResetBio",
        )
        user_before = await UserDAO.get_one_or_none(session, email=email)
        assert user_before is not None

        token = create_action_token(email, "reset", datetime.timedelta(hours=1))

        response = await ac.post(
            "/auth/reset_password",
            json={"token": token, "new_password": new_raw_password},
        )
        assert response.status_code == HTTPStatus.OK

        response_data = response.json()
        assert response_data["message"] == "Password reset successfully"

        user_after = await UserDAO.get_one_or_none(session, email=email)
        assert user_after is not None

        assert user_after.password != hashed
        assert verify_password(new_raw_password, user_after.password)

    async def test_reset_password_handler_fake_email(self, ac: AsyncClient):
        """
        Test password reset endpoint with fake email.

        Expecting 400_BAD_REQUEST with an error message.
        """
        fake_email = "fake_user@example.com"
        fake_token = create_action_token(fake_email, "reset", datetime.timedelta(hours=1))

        response = await ac.post(
            "/auth/reset_password",
            json={"token": fake_token, "new_password": "WhateverPass123"},
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response.json()
