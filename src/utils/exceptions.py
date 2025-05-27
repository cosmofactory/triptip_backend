from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel

from src.settings.config import settings


class ErrorCode(str, Enum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    COULD_NOT_VALIDATE_CREDENTIALS = "COULD_NOT_VALIDATE_CREDENTIALS"
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
    INVALID_TOKEN_TYPE = "INVALID_TOKEN_TYPE"
    INVALID_TOKEN_PAYLOAD = "INVALID_TOKEN_PAYLOAD"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    USER_EXISTS = "USER_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    VIDEO_GENERATION_FAILED = "VIDEO_GENERATION_FAILED"
    INSUFFICIENT_MAIN_BALANCE = "INSUFFICIENT_MAIN_BALANCE"
    WRONG_FILE_SIZE = "WRONG_FILE_SIZE"
    WRONG_IMAGE_DIMENSIONS = "WRONG_IMAGE_DIMENSIONS"
    WRONG_FILE_TYPE = "WRONG_FILE_TYPE"
    USER_ALREADY_VERIFIED = "USER_ALREADY_VERIFIED"
    SUBSCRIPTION_DOES_NOT_EXIST = "SUBSCRIPTION_DOES_NOT_EXIST"
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"


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


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = ErrorCode.INVALID_CREDENTIALS.value):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class CouldNotValidateCredentialsException(HTTPException):
    def __init__(self, detail: str = ErrorCode.COULD_NOT_VALIDATE_CREDENTIALS.value):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidRefreshTokenException(HTTPException):
    def __init__(self, detail: str = ErrorCode.INVALID_REFRESH_TOKEN.value):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class VerificationRequiredException(HTTPException):
    def __init__(self, detail: str = ErrorCode.VERIFICATION_REQUIRED.value):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InvalidTokenTypeException(HTTPException):
    def __init__(self, detail: str = ErrorCode.INVALID_TOKEN_TYPE.value):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidTokenPayloadException(HTTPException):
    def __init__(self, detail: str = ErrorCode.INVALID_TOKEN_PAYLOAD.value):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class TokenExpiredException(HTTPException):
    def __init__(self, detail: str = ErrorCode.TOKEN_EXPIRED.value):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = ErrorCode.INVALID_TOKEN.value):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = ErrorCode.USER_NOT_FOUND.value):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
