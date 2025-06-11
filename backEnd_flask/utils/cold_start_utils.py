from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from database import movies_collection
from models.movie_serializer import movie_serializer


from database import reviews_collection
from typing import List
from bson import ObjectId
import random
from models.movie_serializer import movie_serializer
from motor.motor_asyncio import AsyncIOMotorCollection
async def cold_start_python_filter(
    collection: AsyncIOMotorCollection,
    genres: List[str],
    actors: List[str],
    user_id: str,
    top_n: int = 1000
) -> List[dict]:
    """
    Cold Start: recomendar filmes com base em géneros/atores, excluindo os já avaliados pelo utilizador.
    """
    try:
        query = {
            "$or": [
                {"genres": {"$in": genres}},
                {"cast": {"$in": actors}}
            ]
        }

        # Todos os filmes compatíveis
        movies = await collection.find(query).to_list(length=None)
        if not movies:
            return []

        # Filmes já avaliados por este user
        user_obj_id = ObjectId(user_id)
        rated = await reviews_collection.find({"user_id": user_obj_id}).to_list(length=None)
        rated_movie_ids = {str(r["movie_id"]) for r in rated if ObjectId.is_valid(r["movie_id"])}

        # Filmes que já têm avaliações de qualquer user
        globally_rated_ids = await reviews_collection.distinct("movie_id")
        globally_rated_ids = {str(mid) for mid in globally_rated_ids if ObjectId.is_valid(mid)}

        # Filtrar para manter apenas os que:
        # - têm avaliação global
        # - e ainda NÃO foram avaliados por este utilizador
        filtered_movies = [
            m for m in movies
            if str(m["_id"]) in globally_rated_ids and str(m["_id"]) not in rated_movie_ids
        ]

        if not filtered_movies:
            print(f"[COLD START] Nenhum filme disponível para recomendar ao user {user_id}.")
            return []

        # Ordenar por qualidade
        sorted_movies = sorted(
            filtered_movies,
            key=lambda m: (
                float(m.get("users_review", 0.0) or 0.0),
                float(m.get("imdb_rating", 0) or 0.0),
                int(m.get("votes", 0) or 0)
            ),
            reverse=True
        )

        return [movie_serializer(m) for m in sorted_movies[:top_n]]

    except Exception as e:
        print(f"[COLD START] Erro ao gerar recomendações para {user_id}: {str(e)}")
        return []
