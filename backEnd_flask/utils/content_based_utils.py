from database import movies_collection, reviews_collection, users_collection
from bson import ObjectId
from collections import Counter
from models.movie_serializer import movie_serializer
from typing import List
import statistics

def dice_coefficient(set_a, set_b):
    if not set_a or not set_b:
        return 0
    intersection = len(set_a & set_b)
    return (2 * intersection) / (len(set_a) + len(set_b))

def compute_similarity(movie, top_genres, top_cast, top_directors):
    score = 0
    score += dice_coefficient(set(movie.get("genres", [])), set(top_genres)) * 3
    score += dice_coefficient(set(movie.get("cast", [])), set(top_cast)) * 2
    if movie.get("director") in top_directors:
        score += 1
    return score

async def get_content_based_recommendations(user_id: str, limit: int = 50) -> List[dict] | None:
    try:
        if isinstance(user_id, ObjectId):
            user_obj_id = user_id
        elif ObjectId.is_valid(user_id):
            user_obj_id = ObjectId(user_id)
        else:
            raise ValueError("Invalid user ID")

        user_reviews = await reviews_collection.find({"user_id": user_obj_id}).to_list(None)
        print(f"[CB DEBUG] user_id={user_obj_id} => {len(user_reviews)} reviews encontradas.")
        if not user_reviews:
            return None

        # Garante que movie_ids são todos ObjectId válidos
        movie_ids = [r["movie_id"] for r in user_reviews if isinstance(r["movie_id"], ObjectId)]
        movie_ids_str = {str(mid) for mid in movie_ids}  # ⚠️ usado para garantir exclusão por string
        reviewed_movies = await movies_collection.find({"_id": {"$in": movie_ids}}).to_list(None)
        if not reviewed_movies:
            return None

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

        user = await users_collection.find_one({"_id": user_obj_id})
        if user:
            genres.extend(user.get("preference_genre", []))
            cast.extend(user.get("preference_actor", []))

        avg_runtime = statistics.mean(runtimes) if runtimes else 0
        avg_year = statistics.mean(years) if years else 0
        avg_votes = statistics.mean(votes) if votes else 0
        avg_gross = statistics.mean(gross) if gross else 0

        top_genres = [g for g, _ in Counter(genres).most_common(3)]
        top_cast = [c for c, _ in Counter(cast).most_common(3)]
        top_directors = [d for d, _ in Counter(directors).most_common(2)]

        query = {
            "_id": {"$nin": movie_ids},
            "$or": [
                {"genres": {"$in": top_genres}},
                {"cast": {"$in": top_cast}},
                {"director": {"$in": top_directors}},
            ]
        }

        similar_movies = await movies_collection.find(query).to_list(None)

        filtered_movies = []
        for movie in similar_movies:
            try:
                if "runtime" in movie and movie["runtime"]:
                    runtime = int(movie["runtime"])
                    if avg_runtime and not (avg_runtime * 0.5 <= runtime <= avg_runtime * 1.5):
                        continue
                if "year" in movie and movie["year"]:
                    year = int(movie["year"])
                    if avg_year and not (avg_year - 35 <= year <= avg_year + 35):
                        continue
                if "votes" in movie and movie["votes"]:
                    votes = int(movie["votes"])
                    if avg_votes and votes < avg_votes * 0.1:
                        continue
                if "gross" in movie and movie["gross"]:
                    gross = float(movie["gross"])
                    if avg_gross and gross < avg_gross * 0.05:
                        continue

                movie["cb_score"] = compute_similarity(movie, top_genres, top_cast, top_directors)
                filtered_movies.append(movie)
            except (ValueError, TypeError):
                continue

        if not filtered_movies:
            print(f"[CB] Nenhum filme passou os filtros para {user_id}. Usando todos similares como fallback.")
            filtered_movies = similar_movies

        filtered_movies = [m for m in filtered_movies if m.get("cb_score", 0) >= 1]
        filtered_movies.sort(key=lambda m: m.get("cb_score", 0), reverse=True)

        extra_movies = [
            m for m in similar_movies
            if m.get("cb_score", 0) >= 2 and not any(g in top_genres for g in m.get("genres", []))
        ]
        filtered_movies.extend(extra_movies)

        filtered_movies = [m for m in filtered_movies if str(m["_id"]) not in movie_ids_str]

        assert all(str(m["_id"]) not in movie_ids_str for m in filtered_movies), "⚠️ Filme avaliado passou!"

        # Agrupar por género
        genre_map = {}
        for movie in filtered_movies:
            for genre in movie.get("genres", []):
                genre_map.setdefault(genre, []).append(movie_serializer(movie))

        result = [
            {"genre": genre, "top_movies": movies[:limit]}
            for genre, movies in genre_map.items()
        ]
        return result

    except ValueError as ve:
        print(f"❌ ID inválido: {ve}")
        return None
    except Exception as e:
        print(f"❌ Erro em content_based_utils: {e}")
        return None
