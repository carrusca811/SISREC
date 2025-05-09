from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id: Optional[str]
    title: Optional[str]
    year: Optional[str]
    certificate: Optional[str]
    runtime: Optional[str]
    genres: Optional[List[str]]
    imdb_rating: Optional[str]
    meta_score: Optional[str]
    director: Optional[str]
    cast: Optional[List[str]]
    votes: Optional[str]
    gross: Optional[str]
