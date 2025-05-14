import bcrypt
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import EmailStr, BaseModel
from models.users_model import UserRegister, UserLogin
from models.movie_model import Movie
from database import users_collection, movies_collection
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajusta isso para restringir os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],
)

def convert_to_str(value):
    """ Convert any value to string, except for lists """
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, ObjectId):
        return str(value)
    if value is None:
        return ""
    return str(value)

def movie_serializer(movie) -> dict:
    """ Serializer that converts all fields to strings """
    return {
        "id": str(movie["_id"]),
        "title": convert_to_str(movie.get("title")),
        "year": convert_to_str(movie.get("year")),
        "certificate": convert_to_str(movie.get("certificate")),
        "runtime": convert_to_str(movie.get("runtime")),
        "genres": convert_to_str(movie.get("genres")),
        "imdb_rating": convert_to_str(movie.get("imdb_rating")),
        "meta_score": convert_to_str(movie.get("meta_score")),
        "director": convert_to_str(movie.get("director")),
        "cast": convert_to_str(movie.get("cast")),
        "votes": convert_to_str(movie.get("votes")),
        "gross": convert_to_str(movie.get("gross"))
    }

class UserRegister(BaseModel):
    email: str
    password: str
    preference_genre: Optional[List[str]] = []
    preference_actor: Optional[List[str]] = []

@app.post("/register")
async def register(user: UserRegister):
    print(f"Received payload: {user.dict()}")

    # Verificar se o utilizador já existe
    existing_user = await users_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    # Hash da password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    # Criação do novo utilizador
    new_user = {
        "email": user.email,
        "password": hashed_password.decode("utf-8"),
        "preference_genre": user.preference_genre,
        "preference_actor": user.preference_actor,
        "isSelectingPreferences": True  # Inicialmente True até selecionar preferências
    }

    # Inserir o novo utilizador na base de dados
    try:
        result = await users_collection.insert_one(new_user)

        return {
            "id": str(result.inserted_id),
            "email": user.email,
            "isSelectingPreferences": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(user: UserLogin):
    # Check if the user exists
    existing_user = await users_collection.find_one({"email": user.email})

    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found.")

    # Verify password
    if not bcrypt.checkpw(user.password.encode("utf-8"), existing_user["password"].encode("utf-8")):
        raise HTTPException(status_code=400, detail="Incorrect password.")

    return {
        "id": str(existing_user["_id"]),
        "email": existing_user["email"]
    }

@app.get("/movies", response_model=List[Movie])
async def get_movies():
    try:
        movies = [movie_serializer(movie) async for movie in movies_collection.find()]
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-preferences")
async def update_preferences(preferences: dict):
    user_id = preferences.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")

    try:
        update_data = {
            "preference_genre": preferences.get("preference_genre", []),
            "preference_actor": preferences.get("preference_actor", [])
        }

        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or data not modified.")

        return {"message": "Preferences updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))