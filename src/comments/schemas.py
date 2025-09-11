from pydantic import BaseModel


class SCommentInput(BaseModel):
    "Schema to create a new Comment"

    text: str


class SCommentOutput(BaseModel):
    "Comment output schema"

    id: int
    author_id: int
    trip_id: int
    text: str
