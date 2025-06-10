from database import movies_collection, reviews_collection, users_collection
from bson import ObjectId
from collections import Counter
from models.movie_serializer import movie_serializer
from typing import List
import statistics

async def get_content_based_recommendations(user_id: str, limit: int = 50) -> List[dict]:
    try:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

        user_obj_id = ObjectId(user_id)

        # 1. Reviews do utilizador
        user_reviews = await reviews_collection.find({"user_id": user_obj_id}).to_list(length=None)
        if not user_reviews:
            return []

        movie_ids = [str(r["movie_id"]) for r in user_reviews]
        object_ids = [ObjectId(mid) for mid in movie_ids]

        reviewed_movies = await movies_collection.find({"_id": {"$in": object_ids}}).to_list(length=None)

        if not reviewed_movies:
            return []

        # 2. Características dos filmes avaliados
        genres, cast, directors = [], [], []
        runtimes, years, votes, gross = [], [], [], []

        for movie in reviewed_movies:
            genres.extend(movie.get("genres", []))
            cast.extend(movie.get("cast", []))
            if movie.get("director"):
                directors.append(movie["director"])

            try:
                if movie.get("runtime"): runtimes.append(int(movie["runtime"]))
                if movie.get("year"): years.append(int(movie["year"]))
                if movie.get("votes"): votes.append(int(movie["votes"]))
                if movie.get("gross"): gross.append(float(movie["gross"]))
            except (ValueError, TypeError):
                continue  

        # 3. Preferências explícitas do utilizador
        user = await users_collection.find_one({"_id": user_obj_id})
        if user:
            genres.extend(user.get("preference_genre", []))
            cast.extend(user.get("preference_actor", []))

        # 4. Estatísticas
        avg_runtime = statistics.mean(runtimes) if runtimes else 0
        avg_year = statistics.mean(years) if years else 0
        avg_votes = statistics.mean(votes) if votes else 0
        avg_gross = statistics.mean(gross) if gross else 0

        top_genres = [g for g, _ in Counter(genres).most_common(3)]
        top_cast = [c for c, _ in Counter(cast).most_common(3)]
        top_directors = [d for d, _ in Counter(directors).most_common(2)]

        # 5. Obter candidatos amplos
        query = {
            "_id": {"$nin": object_ids},
            "$or": [
                {"genres": {"$in": top_genres}},
                {"cast": {"$in": top_cast}},
             {"director": {"$in": top_directors}},
            ]   
        }

        similar_movies = await movies_collection.find(query).to_list(length=None)

        # 6. Filtragem fina em Python
        # 6. Filtragem fina em Python (mais tolerante)
        filtered_movies = []
        for movie in similar_movies:
            try:
                if "runtime" in movie and movie["runtime"]:
                    runtime = int(movie["runtime"])
                    if avg_runtime and abs(runtime - avg_runtime) > 40:
                        continue

                if "year" in movie and movie["year"]:
                    year = int(movie["year"])
                    if avg_year and abs(year - avg_year) > 25:
                        continue

                if "votes" in movie and movie["votes"]:
                    votes = int(movie["votes"])
                    if avg_votes and votes < avg_votes * 0.3:  # menos restritivo
                        continue

                if "gross" in movie and movie["gross"]:
                    gross = float(movie["gross"])
                    if avg_gross and gross < avg_gross * 0.3:
                        continue

                filtered_movies.append(movie)

            except (ValueError, TypeError):
                continue  # ignora erros de casting


        # 7. Agrupar por género
        genre_map = {}
        for movie in filtered_movies:
            for genre in movie.get("genres", []):
                genre_map.setdefault(genre, []).append(movie_serializer(movie))

        # 8. Formatar resposta final
        result = [
            {"genre": genre, "top_movies": movies[:limit]}
            for genre, movies in genre_map.items()
        ]

        return result

    except ValueError as ve:
        print(f"❌ ID inválido: {ve}")
        return []
    except Exception as e:
        print(f"❌ Erro em content_based_utils: {e}")
        return []
