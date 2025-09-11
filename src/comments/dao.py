from src.comments.models import Comment
from src.dao.base import BaseDAO


class CommentDAO(BaseDAO):
    model = Comment
