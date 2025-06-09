import bcrypt
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import EmailStr, BaseModel
from models import movie_serializer
from models.review_model import ReviewModel
from models.users_model import UserRegister, UserLogin
from models.movie_model import Movie
from database import users_collection, movies_collection, reviews_collection
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from models.movie_serializer import movie_serializer
from utils.cold_start_utils import cold_start_python_filter
from utils.nonPersonalized import get_top_movies_per_genre
app = FastAPI()
from fastapi import Query, Path
import traceback
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
        "numReviews": 0 
        
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
        "email": existing_user["email"],
        "preference_genre": existing_user.get("preference_genre", []),
        "preference_actor": existing_user.get("preference_actor", []),
        "numReviews": existing_user.get("numReviews", 0),
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
    



@app.get("/movies/cold_start_recommendations", response_model=List[dict])
async def cold_start_recommendations(
    genres: List[str] = Query(..., min_length=1),
    actors: List[str] = Query(..., min_length=1),
    top_n: int = 1000
):
    try:
        return await cold_start_python_filter(movies_collection, genres, actors, top_n)
    except Exception as e:
        print("🔥 ERRO NO BACKEND:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movies/search", response_model=List[dict])
async def search_movies_by_name(name: str = Query(..., min_length=1)):
    try:
        query = {"title": {"$regex": name, "$options": "i"}}
        movies_cursor = movies_collection.find(query)

        results = []
        async for movie in movies_cursor:
            results.append(movie_serializer(movie))
        return results

    except Exception as e:
        import traceback
        print("🔥 ERRO NO BACKEND:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/movies/{id}", response_model=dict)
async def get_movie_by_id(id: str = Path(..., title="Movie ID")):
    from bson import ObjectId

    try:
        movie = await movies_collection.find_one({"_id": ObjectId(id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie_serializer(movie)
    except Exception as e:
        import traceback
        print("🔥 ERRO NO BACKEND:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to fetch movie by ID")
    
@app.post("/movies/review")
async def submit_review(review: ReviewModel):
    try:
        review_doc = {
            "user_id": ObjectId(review.user_id),
            "movie_id": ObjectId(review.movie_id),
            "rating": review.rating,
        }

        # Guarda a nova review
        await reviews_collection.insert_one(review_doc)

        # Incrementa o contador de reviews do utilizador
        await users_collection.update_one(
            {"_id": ObjectId(review.user_id)},
            {"$inc": {"numReviews": 1}}
        )

        return {"message": "Review saved successfully"}

    except Exception as e:
        print("🔥 ERRO AO GUARDAR REVIEW:", str(e))
        raise HTTPException(status_code=500, detail="Error saving review")
