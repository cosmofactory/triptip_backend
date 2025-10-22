from io import BytesIO

import pytest
from fastapi import UploadFile, status

from src.file_service.service import FileService
from src.settings.config import settings


@pytest.mark.asyncio
async def test_file_uploading(monkeypatch):
    """
    Test that the file is uploaded to the S3 bucket and the URL of the uploaded file is returned.

    Test the file is stored in the bucket with the name of a UUID and the extension of the file.
    """

    async def mock_upload_file(self, file):
        extension = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
        return (
            f"https://{settings.AWS_CLOUDFRONT_DISTRIBUTION}/trip_photos/faked_uuid_123.{extension}"
        )

    monkeypatch.setattr("src.file_service.service.FileService.upload_file", mock_upload_file)

    file_service = FileService("test_bucket")
    headers = {"content-type": "image/jpeg"}
    file = UploadFile(filename="test.jpg", file=BytesIO(b"test"), headers=headers)
    url = await file_service.upload_file(file)
    assert url == f"https://{settings.AWS_CLOUDFRONT_DISTRIBUTION}/trip_photos/faked_uuid_123.jpg"


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
@pytest.mark.asyncio
async def test_file_uploading_endpoint(mock_file_upload, authenticated_ac, content_type, expected):
    """
    Test file uploading endpoint.

    Test that the file is uploaded to the S3 bucket and the URL of the uploaded file is returned.
    Test the file is stored in the bucket with the name of a UUID and the extension of the file.
    Test only allowed file types are accepted.
    """
    with open("tests/mock_data/test_file.jpg", "rb") as f:
        response = await authenticated_ac.post(
            "/users/profile/me/userpic", files={"file": ("filename", f, content_type)}
        )
    assert response.status_code == expected
    if expected == status.HTTP_201_CREATED:
        response_data = response.json()
        assert "userpic" in response_data
        assert response_data["userpic"] is not None
