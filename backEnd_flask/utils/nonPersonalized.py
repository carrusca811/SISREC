from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

async def get_top_movies_per_genre(
    collection: AsyncIOMotorCollection,
    limit: int = 10
) -> List[dict]:
    """
    Gera recomendações não personalizadas com os filmes mais populares por género.
    """
    try:
        pipeline = [
            {"$unwind": "$genres"},
            {"$sort": {"imdb_rating": -1}},
            {"$group": {
                "_id": "$genres",
                "top_movies": {"$push": {
                    "id": "$_id",
                    "title": "$title",
                    "imdb_rating": "$imdb_rating",
                    "cast": "$cast",
                    "year": "$year",
                    "genres": "$genres",
                    "image_url": "$image_url"
                }}
            }},
            {"$project": {
                "genre": "$_id",
                "top_movies": {"$slice": ["$top_movies", limit]},
                "_id": 0
            }}
        ]

        result = await collection.aggregate(pipeline).to_list(length=None)

        # Converte ObjectId para string e aplica validação extra
        for genre_group in result:
            for movie in genre_group["top_movies"]:
                movie_id = movie.get("id")
                if isinstance(movie_id, ObjectId):
                    movie["id"] = str(movie_id)

        return result

    except Exception as e:
        print(f"[NON-PERSONALIZED] Error generating genre-based recommendations: {str(e)}")
        return []
