from typing import Type

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.file_service.service import FileService
from src.settings.config import settings
from src.users.models import User
from src.utils.exceptions import PermissionError
from src.utils.utils import check_file_size, check_file_type


class Permissions:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_author_or_read_only(
        self, obj_id: int, dao_class: Type[BaseDAO], user: User
    ) -> None:
        obj = await dao_class.get_object_or_404(self.db, id=obj_id)
        if obj.author_id != user.id:
            raise PermissionError

    @staticmethod
    async def check_is_admin(user: User):
        if not user.is_admin:
            raise PermissionError


async def upload_image(file: UploadFile) -> str | None:
    """
    Upload image to the AWS S3 bucket.

    File size and type should be in accordance with the settings.
    :param file: File to upload.
    :return: URL to the uploaded image.
    """
    await check_file_type(file.content_type)
    await check_file_size(file.size)
    file_service = FileService(bucket_name=settings.AWS_BUCKET_NAME)
    return await file_service.upload_file(file)
