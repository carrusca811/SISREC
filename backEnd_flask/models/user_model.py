from pydantic import BaseModel

class User(BaseModel):
    email: str
    preferenceGenre: list[str]  # Exemplo: ["Action", "Sci-Fi", "Drama"]
    preferenceActor: list[str]  # Exemplo: ["Actor1", "Actor2", "Actor3"]
