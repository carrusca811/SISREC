import random
from database import users_collection, movies_collection
from bson import ObjectId
from typing import List
from fastapi import Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from database import movies_collection  
from models.movie_model import Movie
from models.movie_serializer import movie_serializer




def get_popular_movies(limit=10):
    """
    Get the most popular movies based on ratings.
    """
    try:
        movies = list(movies_collection.find().sort("imdb_rating", -1).limit(limit))
        return movies
    except Exception as e:
        print(f"Error retrieving popular movies: {str(e)}")
        return []

def recommend_based_on_preferences(user):
    """
    Recommend movies based on user preferences (genre and actor).
    """
    try:
        query = {}
        if user.get("preference_genre"):
            query["genres"] = {"$in": user["preference_genre"]}
        if user.get("preference_actor"):
            query["cast"] = {"$in": user["preference_actor"]}
        
        recommended_movies = list(movies_collection.find(query).limit(10))
        
        # Fallback to popular movies if no match
        if not recommended_movies:
            recommended_movies = get_popular_movies()

        return recommended_movies
    except Exception as e:
        print(f"Error recommending movies: {str(e)}")
        return []

async def cold_start_python_filter(
    collection: AsyncIOMotorCollection,
    genres: List[str],
    actors: List[str],
    top_n: int = 1000
) -> List[dict]:
    all_movies = await collection.find({}).to_list(length=None)

    # Filtra os filmes com pelo menos um género ou um ator em comum
    filtered = [
        movie for movie in all_movies
        if (
            any(g.lower() in [m.lower() for m in movie.get("genres", [])] for g in genres)
            or
            any(a.lower() in [c.lower() for c in movie.get("cast", [])] for a in actors)
        )
    ]

    # Ordena por imdb_rating e votos
    sorted_movies = sorted(
        filtered,
        key=lambda x: (x.get("imdb_rating", 0), x.get("votes", 0)),
        reverse=True
    )

    # Serializa e adiciona poster
    results = []
    for movie in sorted_movies[:top_n]:
        serialized = movie_serializer(movie)
        results.append(serialized)

    return results