from src.settings.config import settings
from src.utils.exceptions import FileIsTooLarge, WrongFileType


async def check_file_type(file_type: str) -> None:
    """Check if the file type that is being uploaded is allowed in our settings."""
    if file_type not in settings.ALLOWED_CONTENT_TYPES:
        raise WrongFileType


async def check_file_size(file_size: int) -> None:
    """Check if the file size that is being uploaded is allowed in our settings."""
    if file_size > settings.MAX_FILE_SIZE:
        raise FileIsTooLarge
