from src.dao.base import BaseDAO
from src.users.models import User


class AuthDAO(BaseDAO):
    model = User
