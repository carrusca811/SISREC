from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

async def get_top_movies_per_genre(collection: AsyncIOMotorCollection, limit: int = 10) -> List[dict]:
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

    # Convert ObjectId to str
    for genre_group in result:
        for movie in genre_group["top_movies"]:
            if isinstance(movie["id"], ObjectId):
                movie["id"] = str(movie["id"])

    return result
