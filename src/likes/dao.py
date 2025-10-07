from src.dao.base import BaseDAO
from src.likes.models import Like


class LikeDAO(BaseDAO):
    model = Like
