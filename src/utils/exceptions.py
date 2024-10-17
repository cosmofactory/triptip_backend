from fastapi import HTTPException, status
from pydantic import BaseModel

from src.settings.config import settings


class SErrorResponse(BaseModel):
    detail: str


class WrongFileType(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only JPEG, PNG, GIF, and WEBP are allowed.",
        )


class FileIsTooLarge(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is too large. Maximum file size is {settings.MAX_FILE_SIZE} MB.",
        )


class PermissionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )
