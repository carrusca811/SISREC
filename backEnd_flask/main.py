import bcrypt
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import EmailStr, BaseModel
from models.users_model import UserRegister, UserLogin
from models.movie_model import Movie
from database import users_collection, movies_collection
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

from utils.nonPersonalized import get_top_movies_per_genre

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
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

from bson import ObjectId

def movie_serializer(movie):
    return {
        "id": str(movie["_id"]),
        "title": movie["title"],
        "year": movie["year"],
        "certificate": movie["certificate"],
        "runtime": movie["runtime"],
        "genres": movie["genres"],
        "imdb_rating": movie["imdb_rating"],
        "meta_score": movie["meta_score"],
        "director": movie["director"],
        "cast": movie["cast"],
        "votes": movie["votes"],
        "gross": movie["gross"]
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



@app.get("/movies/non_personalized_recommendations", response_model=List[dict])
async def get_non_personalized_movies():
    try:
        results = await get_top_movies_per_genre(movies_collection)
        return results
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