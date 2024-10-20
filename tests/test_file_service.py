import uuid
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile, status

from src.file_service.service import FileService


@pytest.mark.asyncio
async def test_file_uploading(aws_credentials, mock_aws, mock_s3_bucket, monkeypatch):
    """
    Test that the file is uploaded to the S3 bucket and the URL of the uploaded file is returned.

    Test the file is stored in the bucket with the name of a UUID and the extension of the file.
    """
    file_service = FileService("test_bucket")
    headers = {"content-type": "image/jpeg"}
    file = UploadFile(filename="test.jpg", file=BytesIO(b"test"), headers=headers)
    monkeypatch.setattr(uuid, "uuid4", MagicMock(return_value="faked_uuid_123"))
    url = await file_service.upload_file(file)
    assert url == "https://test_bucket.s3.us-east-1.amazonaws.com/trip_photos/faked_uuid_123.jpg"
    s3_objects = mock_s3_bucket.list_objects(Bucket="test_bucket")
    assert s3_objects["Contents"][0]["Key"] == "trip_photos/faked_uuid_123.jpg"


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
async def test_file_uploading_endpoint(
    aws_credentials, mock_aws, mock_s3_bucket, monkeypatch, authenticated_ac, content_type, expected
):
    """
    Test file uploading endpoint.

    Test that the file is uploaded to the S3 bucket and the URL of the uploaded file is returned.
    Test the file is stored in the bucket with the name of a UUID and the extension of the file.
    Test only allowed file types are accepted.
    """

    monkeypatch.setattr(uuid, "uuid4", MagicMock(return_value="uploaded_image_123"))
    with open("tests/mock_data/test_file.jpg", "rb") as f:
        response = await authenticated_ac.post(
            "/users/profile/me/userpic_upload", files={"file": ("filename", f, content_type)}
        )
    s3_objects = mock_s3_bucket.list_objects(Bucket="test_bucket")
    assert response.status_code == expected
    if expected == status.HTTP_201_CREATED:
        assert s3_objects["Contents"][0]["Key"] == "trip_photos/uploaded_image_123.jpg"
