from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import users_collection
from recommender import generate_recommendations

app = FastAPI()

class RecommendationRequest(BaseModel):
    email: str
    preferences: list[str]

@app.post("/register")
def register_user(user: RecommendationRequest):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    # Simulação de um dataset (em vez de MongoDB, usa um dataset real mais tarde)
    dataset = [
        {"item": "Matrix", "Action": 1, "Sci-Fi": 1, "Drama": 0},
        {"item": "Inception", "Action": 1, "Sci-Fi": 1, "Drama": 1},
        {"item": "Titanic", "Action": 0, "Sci-Fi": 0, "Drama": 1},
        {"item": "Star Wars", "Action": 1, "Sci-Fi": 1, "Drama": 0},
        {"item": "Oppenheimer", "Action": 0, "Sci-Fi": 0, "Drama": 1}
    ]

    recommendations = generate_recommendations(request.preferences, dataset)
    return {"recommendations": recommendations}
