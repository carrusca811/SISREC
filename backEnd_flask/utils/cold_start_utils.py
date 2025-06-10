from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from database import movies_collection
from models.movie_serializer import movie_serializer


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
        # Ordenar por users_review, imdb_rating, depois votes
        sorted_movies = sorted(
            movies,
            key=lambda m: (
                float(m.get("users_review", 0.0) or 0.0),
                float(m.get("imdb_rating", 0) or 0.0),
                int(m.get("votes", 0) or 0)
            ),
            reverse=True
        )


        # Serializar resultados
        return [movie_serializer(movie) for movie in sorted_movies[:top_n]]

    except Exception as e:
        print(f"[COLD START] Error: {str(e)}")
        return []
