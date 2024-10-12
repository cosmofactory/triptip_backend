import uuid
from io import BytesIO
from unittest.mock import MagicMock

import boto3
import pytest
from fastapi import UploadFile
from moto import mock_aws as aws

from src.file_service.service import FileService


@pytest.mark.asyncio
async def test_file_uploading(aws_credentials, mock_aws, monkeypatch):
    with aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test_bucket")
        file_service = FileService("test_bucket")
        headers = {"content-type": "image/jpeg"}
        file = UploadFile(filename="test.jpg", file=BytesIO(b"test"), headers=headers)
        monkeypatch.setattr(uuid, "uuid4", MagicMock(return_value="faked_uuid_123"))
        url = await file_service.upload_file(file)
        assert (
            url == "https://test_bucket.s3.us-east-1.amazonaws.com/trip_photos/faked_uuid_123.jpg"
        )
        s3_objects = s3.list_objects(Bucket="test_bucket")
        assert s3_objects["Contents"][0]["Key"] == "trip_photos/faked_uuid_123.jpg"
