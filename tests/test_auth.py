import asyncio
import datetime
from http import HTTPStatus

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import create_email_verification_token, get_password_hash
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

        token = create_email_verification_token(email, datetime.timedelta(hours=1))

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
        token = create_email_verification_token(email, expires_delta)
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload.get("sub") == email
        assert payload.get("verify") is True

        now = datetime.datetime.now(datetime.timezone.utc)
        token_exp = datetime.datetime.fromtimestamp(payload.get("exp"), tz=datetime.timezone.utc)

        expected_exp = now + expires_delta
        time_difference = abs((token_exp - expected_exp).total_seconds())
        assert time_difference < 2, f"Expiration delta {time_difference} exceeded allowed tolerance"

    async def test_resend_verification_email_success(self, ac: AsyncClient, session: AsyncSession):
        """
        Test successful resending verification email.

        1. Create an unverified user.
        2. Call /auth/resend_verification.
        3. Ensure a 202 ACCEPTED with success message and expiritation time.
        """
        email = "resend_test@example.com"
        raw_password = "ResendPass123"
        hashed = get_password_hash(raw_password)
        await UserDAO.create(
            session,
            email=email,
            username="ResendUser",
            password=hashed,
            bio="ResendBioTest",
            is_verified=False,
        )

        user = await UserDAO.get_one_or_none(session, email=email)
        assert user is not None
        assert user.is_verified is False

        response = await ac.post(
            "/auth/resend_verification",
            json={"email": email},
        )
        assert response.status_code == HTTPStatus.ACCEPTED

        response_data = response.json()
        assert response_data["message"] == "Verification email sent successfully"
        assert response_data["email"] == email
        assert "expires_in_hours" in response_data

    async def test_resed_verification_email_failure(self, ac: AsyncClient):
        """
        Test resending verification email failure.

        1. Call /auth/resend_verification with a non-existent email.
        2. Ensure a 404 NOT_FOUND with an error message.
        """
        response = await ac.post(
            "/auth/resend_verification",
            json={"email": "non_existent@example.com"},
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "does not exist" in response.json()["detail"]

    async def test_resed_verification_email_already_verified(
        self, ac: AsyncClient, session: AsyncSession
    ):
        """
        Test resending verification email for an already verified user.

        1. Create a verified user.
        2. Call /auth/resend_verification.
        3. Ensure a 400 BAD_REQUEST with an error message.
        """
        email = "already_verified@example.com"
        raw_password = "AlreadyVerified"
        hashed = get_password_hash(raw_password)
        await UserDAO.create(
            session,
            email=email,
            username="AlreadyVerifiedUser",
            password=hashed,
            bio="I am verified",
            is_verified=True,
        )

        user = await UserDAO.get_one_or_none(session, email=email)
        assert user is not None
        assert user.is_verified is True

        response = await ac.post("/auth/resend_verification", json={"email": email})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "already verified" in response.json()["detail"]
