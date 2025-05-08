from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    title: str
    year: int
    certificate: Optional[str]
    runtime: int
    genres: List[str]
    imdb_rating: float
    meta_score: Optional[int]
    director: str
    cast: List[str]
    votes: int
    gross: Optional[float]
