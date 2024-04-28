from src.dao.base import BaseDAO
from src.users.models import User


class UserDAO(BaseDAO):
    model = User
