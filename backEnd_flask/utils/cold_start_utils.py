from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from database import movies_collection
from models.movie_serializer import movie_serializer


def get_popular_movies(limit: int = 10) -> List[dict]:
    """
    Get the most popular movies based on IMDb rating.
    """
    try:
        movies = movies_collection.find().sort("imdb_rating", -1).limit(limit)
        return [movie_serializer(m) for m in movies]
    except Exception as e:
        print(f"[POPULAR] Error retrieving popular movies: {str(e)}")
        return []


def recommend_based_on_preferences(user: dict, limit: int = 10) -> List[dict]:
    """
    Recommend movies based on saved user preferences (genre and actor).
    """
    try:
        query = {}
        if user.get("preference_genre"):
            query["genres"] = {"$in": user["preference_genre"]}
        if user.get("preference_actor"):
            query["cast"] = {"$in": user["preference_actor"]}

        cursor = movies_collection.find(query).limit(limit)
        recommended_movies = [movie_serializer(m) for m in cursor]

        if not recommended_movies:
            return get_popular_movies(limit)

        return recommended_movies
    except Exception as e:
        print(f"[PREFERENCES] Error recommending movies: {str(e)}")
        return get_popular_movies(limit)


async def cold_start_python_filter(
    collection: AsyncIOMotorCollection,
    genres: List[str],
    actors: List[str],
    top_n: int = 1000
) -> List[dict]:
    """
    Recommend movies for new users (cold start), based on genre or actor preferences.
    """
    try:
        query = {
            "$or": [
                {"genres": {"$in": genres}},
                {"cast": {"$in": actors}}
            ]
        }

        # Query MongoDB with filter
        movies = await collection.find(query).to_list(length=None)

        # Ordenar por imdb_rating (float) e votes (int)
        sorted_movies = sorted(
            movies,
            key=lambda m: (
                float(m.get("imdb_rating", 0) or 0),
                int(m.get("votes", 0) or 0)
            ),
            reverse=True
        )

        # Serializar resultados
        return [movie_serializer(movie) for movie in sorted_movies[:top_n]]

    except Exception as e:
        print(f"[COLD START] Error: {str(e)}")
        return []
