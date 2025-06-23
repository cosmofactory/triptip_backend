import uuid

import aioboto3
import logfire
from fastapi import UploadFile

from src.settings.config import settings


class FileService:
    def __init__(self, bucket_name: str):
        self.session: aioboto3.Session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name: str = bucket_name
        self.image_folder: str = "trip_photos"

    @logfire.instrument()
    async def upload_file(self, file: UploadFile):
        """
        Uploads a file to the S3 bucket and returns the URL of the uploaded file.

        :param file: File to upload
        File will be stored in the bucket with the name of a UUID and the extension of the file.
        """
        extension = file.filename.rsplit(".", 1)[-1]
        key = f"{self.image_folder}/{uuid.uuid4()}.{extension}"

        async with self.session.client(service_name="s3") as s3_client:
            await s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                key,
                ExtraArgs={
                    "ContentType": file.content_type or "application/octet-stream",
                },
            )
        return f"https://{settings.AWS_CLOUDFRONT_DISTRIBUTION}/{key}"
