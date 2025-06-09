from pydantic import BaseModel, EmailStr
from typing import List

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    preference_genre: List[str] = []
    preference_actor: List[str] = []
    numReviews: int = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str
