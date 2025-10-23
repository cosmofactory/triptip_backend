from http import HTTPStatus

import pytest
from fastapi import status
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

    async def test_follow_yourself(self, authenticated_ac: AsyncClient):
        """
        Attempting to follow yourself should return 400 Bad Request.
        """
        user_id = authenticated_ac.user.id
        assert user_id is not None

        response = await authenticated_ac.post(f"/users/profile/{user_id}/follow")
        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_follow_user(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
    ):
        """
        Following another user should return 202 Accepted and subscription info.
        """
        followee = await UserFactory.create(db=session)
        assert followee is not None

        response = await authenticated_ac.post(f"/users/profile/{followee.id}/follow")
        assert response.status_code == HTTPStatus.ACCEPTED

        response_data = response.json()

        assert response_data["follower_id"] == authenticated_ac.user.id
        assert response_data["followee_id"] == followee.id

    async def test_unfollow_user(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
    ):
        """
        Expected 204_NO_CONTENT while attempting to unfollow user.
        """
        followee = await UserFactory.create(db=session)
        assert followee is not None

        response = await authenticated_ac.delete(f"/users/profile/{followee.id}/follow")
        assert response.status_code == HTTPStatus.NO_CONTENT

    async def test_follow_user_duplicate(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
    ):
        """
        Expected 400_BAD_REQUEST while attempting to follow second time.
        """
        followee = await UserFactory.create(db=session)
        assert followee is not None

        cleanup_response = await authenticated_ac.delete(f"/users/profile/{followee.id}/follow")
        assert cleanup_response.status_code == HTTPStatus.NO_CONTENT

        # First follow attempt
        response_1 = await authenticated_ac.post(f"/users/profile/{followee.id}/follow")
        assert response_1.status_code == HTTPStatus.ACCEPTED

        # Second follow must be rejected
        response_2 = await authenticated_ac.post(f"/users/profile/{followee.id}/follow")
        assert response_2.status_code == HTTPStatus.BAD_REQUEST

    async def test_unfollow_yourself(self, authenticated_ac: AsyncClient):
        """
        Expected 400_BAD_REQUEST while attempting to unfollow yourself.
        """
        user_id = authenticated_ac.id
        assert user_id is not None

        response = await authenticated_ac.delete(f"/users/profile/{user_id}/follow")
        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_followings_list(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
    ):
        """
        Followings list should reflect current subscriptions.

        1. Start empty.
        2. Follow two users.
        3. Verify they appear.
        4. Unfollow and verify removal.
        """
        user_id = authenticated_ac.id
        assert user_id is not None

        response_1 = await authenticated_ac.get(f"/users/profile/{user_id}/followings")
        assert response_1.status_code == HTTPStatus.OK

        # Create two new users
        user_1 = await UserFactory.create(db=session)
        assert user_1 is not None

        user_2 = await UserFactory.create(db=session)
        assert user_2 is not None

        followee_ids = {user_1.id, user_2.id}

        # Follow both users
        for ids in followee_ids:
            await authenticated_ac.post(f"/users/profile/{ids}/follow")

        # Verify followings include the new followees
        response_2 = await authenticated_ac.get(f"/users/profile/{user_id}/followings")
        assert response_2.status_code == HTTPStatus.OK

        response_data = response_2.json()
        result_ids = {user["id"] for user in response_data["users"]}
        assert followee_ids.issubset(result_ids)

        # Unfollow and verify that users are removed
        for ids in followee_ids:
            delete_resp = await authenticated_ac.delete(f"/users/profile/{ids}/follow")
            assert delete_resp.status_code == HTTPStatus.NO_CONTENT

        response_3 = await authenticated_ac.get(f"/users/profile/{user_id}/followings")
        assert response_3.status_code == HTTPStatus.OK

        result_ids_after_deletions = {user["id"] for user in response_3.json()["users"]}
        assert followee_ids.isdisjoint(result_ids_after_deletions)

    @pytest.mark.parametrize(
        "content_type, expected",
        [
            (
                "image/png",
                status.HTTP_201_CREATED,
            ),
            (
                "image/jpeg",
                status.HTTP_201_CREATED,
            ),
            (
                "image/jpg",
                status.HTTP_201_CREATED,
            ),
            (
                "text/css",
                status.HTTP_400_BAD_REQUEST,
            ),
            (
                "application/x-bat",
                status.HTTP_400_BAD_REQUEST,
            ),
            (
                "application/x-sh",
                status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    async def test_upload_userpic(
        self,
        authenticated_ac: AsyncClient,
        mock_file_upload,
        content_type,
        expected,
    ):
        """
        Expecting 201_CREATED for uploading userpic.
        """
        assert authenticated_ac is not None

        with open("tests/mock_data/test_file.jpg", "rb") as f:
            response = await authenticated_ac.post(
                "/users/profile/me/userpic", files={"file": ("filename", f, content_type)}
            )
        assert response.status_code == expected
        if expected == HTTPStatus.CREATED:
            response_data = response.json()
            assert "userpic" in response_data
            assert response_data["userpic"] is not None

    @pytest.mark.parametrize(
        "content_type",
        [
            "image/png",
            "image/jpeg",
            "image/jpg",
            "text/css",
            "application/x-bat",
            "application/x-sh",
        ],
    )
    async def test_upload_userpic_unauthorized(
        self,
        ac: AsyncClient,
        session: AsyncSession,
        mock_file_upload,
        content_type,
    ):
        """
        Test upload a userpic for unauthorized user.

        Expecting 401_UNAUTHORIZED.
        """
        user = await UserFactory.create(db=session)
        assert user is not None

        with open("tests/mock_data/test_file.jpg", "rb") as f:
            response = await ac.post(
                "/users/profile/me/userpic", files={"file": ("filename", f, content_type)}
            )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_update_userpic(self, authenticated_ac: AsyncClient, mock_file_upload):
        """
        Update userpic:
            1. Upload userpic at 1st time.
            2. Check if userpic is uploaded -> expecting 201_CREATED.
            3. Update userpic -> expecting 200_OK.
            4. Check if userpic is updated.
            5. Check that only userpic is updated.
        """
        assert authenticated_ac is not None

        with open("tests/mock_data/test_file.jpg", "rb") as f:
            upload_response = await authenticated_ac.post(
                "/users/profile/me/userpic", files={"file": ("filename", f, "image/jpeg")}
            )
        assert upload_response.status_code == HTTPStatus.CREATED

        upload_response_data = upload_response.json()
        assert "userpic" in upload_response_data
        assert upload_response_data["userpic"] is not None

        first_userpic = upload_response_data["userpic"]

        with open("tests/mock_data/test_file.jpg", "rb") as f:
            update_response = await authenticated_ac.patch(
                "/users/profile/me/userpic", files={"file": ("filename", f, "image/jpeg")}
            )
        assert update_response.status_code == HTTPStatus.OK

        update_response_data = update_response.json()
        assert "userpic" in update_response_data
        assert update_response_data["userpic"] is not None

        assert update_response_data["userpic"] != first_userpic

        for key in upload_response_data.keys():
            if key in update_response_data and key != "userpic":
                assert upload_response_data[key] == update_response_data[key]

    async def test_update_userpic_unauthorized(self, ac: AsyncClient):
        """
        Test update userpic for unauthorized user.

        Expecting 401_UNAUTHORIZED.
        """
        assert ac is not None

        with open("tests/mock_data/test_file.jpg", "rb") as f:
            response = await ac.patch(
                "/users/profile/me/userpic", files={"file": ("filename", f, "image/jpeg")}
            )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
