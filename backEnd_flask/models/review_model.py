
from typing import Optional
from pydantic import BaseModel


class ReviewModel(BaseModel):
    user_id: str
    movie_id: str
    rating: int
