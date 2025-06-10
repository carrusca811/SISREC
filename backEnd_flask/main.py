import asyncio
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
from bson.errors import InvalidId
from fastapi.middleware.cors import CORSMiddleware
from models.movie_serializer import movie_serializer
from utils.colaborative_filtering_utils import build_user_movie_matrix, recommend_movies_for_user
from utils.cold_start_utils import cold_start_python_filter
from utils.nonPersonalized import get_top_movies_per_genre

app = FastAPI()
from fastapi import Query, Path
import traceback
from fastapi.middleware.cors import CORSMiddleware
import logging
from utils.colaborative_als import build_als_training_data, build_als_model, recommend_movies_als
logger = logging.getLogger("hybrid_recommendation")
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"



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



    
@app.post("/movies/review")
async def submit_review(review: ReviewModel):
    try:
        user_obj_id = ObjectId(review.user_id)
        movie_obj_id = ObjectId(review.movie_id)

        # 1. Substitui ou insere a review (1 review por utilizador-filme)
        result = await reviews_collection.update_one(
            {"user_id": user_obj_id, "movie_id": movie_obj_id},
            {"$set": {"rating": review.rating}},
            upsert=True
        )

        # 2. Se foi inserida pela primeira vez, incrementa o contador do utilizador
        if result.upserted_id:
            await users_collection.update_one(
                {"_id": user_obj_id},
                {"$inc": {"numReviews": 1}}
            )

        # 3. Recalcula a média
        all_reviews = await reviews_collection.find(
            {"movie_id": movie_obj_id}
        ).to_list(length=None)

        if all_reviews:
            avg_rating = sum(r.get("rating", 0) for r in all_reviews) / len(all_reviews)
        else:
            avg_rating = 0.0

        # 4. Atualiza a média no filme
        await movies_collection.update_one(
            {"_id": movie_obj_id},
            {"$set": {"users_review": avg_rating}}
        )

        return {"message": "Review saved and movie updated successfully"}

    except Exception as e:
        print("🔥 ERRO AO GUARDAR REVIEW:", str(e))
        raise HTTPException(status_code=500, detail="Error saving review")


from utils.content_based_utils import get_content_based_recommendations

@app.get("/movies/content_based_recommendations", response_model=List[dict])
async def content_based_recommendations(user_id: str = Query(...)):
    try:
        return await get_content_based_recommendations(user_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    except Exception as e:
        import traceback
        print("🔥 ERRO CONTENT BASED ENDPOINT:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao gerar recomendações content-based.")
    


"""
@app.get("/movies/collaborative_recommendations", response_model=List[dict])
async def collaborative_recommendations(user_id: str = Query(...)):
    try:
        matrix = await build_user_movie_matrix()
        recommended_ids = recommend_movies_for_user(matrix, user_id)

        # Buscar filmes por ID
        from bson import ObjectId
        movies = await movies_collection.find({
            "_id": {"$in": [ObjectId(m) for m in recommended_ids]}
        }).to_list(None)

        return [movie_serializer(m) for m in movies]
    except Exception as e:
        print(f"🔥 ERRO COLLAB FILTERING: {e}")
        raise HTTPException(status_code=500, detail="Erro no sistema de recomendação colaborativo.")
        """

@app.get("/movies/hybrid_recommendations", response_model=List[dict])
async def hybrid_recommendations(user_id: str = Query(...)):
    try:
        user_obj_id = ObjectId(user_id)

        # 1. Filmes já avaliados
        reviewed_movies_cursor = await reviews_collection.find(
            {"user_id": user_obj_id}, {"movie_id": 1}
        ).to_list(None)
        reviewed_ids = {str(r["movie_id"]) for r in reviewed_movies_cursor}

        # 2. ALS + Content-Based em paralelo
        df_matrix_task = build_als_training_data()
        content_task = get_content_based_recommendations(user_id)
        (df, user_movie_matrix), content_based = await asyncio.gather(df_matrix_task, content_task)

        model, uid_map, mid_rev_map, als_matrix = build_als_model(df, user_movie_matrix)
        als_recommendations = recommend_movies_als(model, als_matrix, uid_map, mid_rev_map, user_id)

        # 3. Buscar detalhes dos filmes ALS que não foram avaliados
        als_movie_ids = [ObjectId(mid) for mid, _ in als_recommendations if mid not in reviewed_ids]
        collaborative_movies = await movies_collection.find({
            "_id": {"$in": als_movie_ids}
        }).to_list(None)

        score_map = dict(als_recommendations)
        serialized_collab = []
        for m in collaborative_movies:
            movie = movie_serializer(m)
            movie["hybrid_score"] = 0.7
            movie["als_score"] = score_map.get(str(m["_id"]), 0)
            serialized_collab.append(movie)

        # 4. Mapear Content-Based
        combined_map = {}
        for group in content_based:
            for movie in group["top_movies"]:
                movie_id = str(movie["id"])
                if movie_id not in reviewed_ids:
                    movie["hybrid_score"] = 0.3
                    combined_map[movie_id] = movie

        # 5. Fundir com ALS
        for movie in serialized_collab:
            movie_id = str(movie["id"])
            if movie_id not in reviewed_ids:
                if movie_id in combined_map:
                    combined_map[movie_id]["hybrid_score"] += 0.7
                else:
                    combined_map[movie_id] = movie

        if not combined_map:
            logger.warning(f"Sem recomendações para user_id={user_id}, a devolver populares.")
            return await fallback_popular_grouped()

        # 6. Agrupar por género
        genre_map = {}
        for movie in combined_map.values():
            for genre in movie.get("genres", []):
                genre_map.setdefault(genre, []).append(movie)

        result = []
        for genre, movies in genre_map.items():
            for m in movies:
                m["popularity_score"] = m.get("users_review", 0)

            movies_sorted = sorted(
                movies,
                key=lambda x: (x.get("hybrid_score", 0), x.get("popularity_score", 0)),
                reverse=True
            )

            selected = movies_sorted[:10]
            existing_ids = {str(m["id"]) for m in selected}

            # Preencher se necessário
            ignore_ids = []
            for mid in reviewed_ids.union(existing_ids):
                try:
                    ignore_ids.append(ObjectId(mid))
                except Exception:
                    continue

            if len(selected) < 10:
                extra_movies = await movies_collection.find({
                    "genres": genre,
                    "_id": {"$nin": ignore_ids}
                }).sort("users_review", -1).limit(10 - len(selected)).to_list(None)
                serialized_extra = [movie_serializer(m) for m in extra_movies]
                selected.extend(serialized_extra)

            selected = [m for m in selected if str(m["id"]) not in reviewed_ids]

            result.append({
                "genre": genre,
                "top_movies": selected[:10]
            })

        return result

    except Exception:
        logger.error("Erro ao gerar recomendações híbridas", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao gerar recomendações híbridas.")


# --- Fallback: populares por género (sem histórico)
async def fallback_popular_grouped(limit_per_genre: int = 10) -> List[dict]:
    genres = await movies_collection.distinct("genres")
    result = []
    for genre in genres:
        popular_movies = await movies_collection.find({
            "genres": genre
        }).sort("users_review", -1).limit(limit_per_genre).to_list(None)
        result.append({
            "genre": genre,
            "top_movies": [movie_serializer(m) for m in popular_movies]
        })
    return result



@app.get("/users/{id}", response_model=dict)
async def get_user_by_id(id: str):    
        try:
            if not ObjectId.is_valid(id):
                raise HTTPException(status_code=400, detail="Invalid user ID")
            user = await users_collection.find_one({"_id": ObjectId(id)})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user["id"] = str(user["_id"])
            user.pop("_id", None)
            return user
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        except Exception as e:
            print(f"❌ Erro ao buscar utilizador: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
        
@app.get("/users/{id}/reviewed-movies", response_model=List[dict])
async def get_user_reviewed_movies(id: str = Path(..., title="User ID")):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid user ID")

        user_obj_id = ObjectId(id)

        # Buscar reviews do utilizador com movie_id e rating
        user_reviews = await reviews_collection.find(
            {"user_id": user_obj_id}, {"movie_id": 1, "rating": 1}
        ).to_list(length=None)

        if not user_reviews:
            return []

        movie_ids = [r["movie_id"] for r in user_reviews]

        # Buscar os filmes
        movies = await movies_collection.find({"_id": {"$in": movie_ids}}).to_list(length=None)

        # Mapear reviews para lookup rápido
        rating_map = {str(r["movie_id"]): r["rating"] for r in user_reviews}

        # Serializar com rating incluído
        from models.movie_serializer import movie_serializer
        enriched_movies = []
        for movie in movies:
            serialized = movie_serializer(movie)
            serialized["user_rating"] = rating_map.get(str(movie["_id"]), None)
            enriched_movies.append(serialized)

        return enriched_movies

    except Exception as e:
        print("🔥 ERRO AO BUSCAR FILMES AVALIADOS:", e)
        raise HTTPException(status_code=500, detail="Erro ao buscar filmes avaliados.")
    
    
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
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid movie ID format")
    
@app.get("/evaluate")
async def trigger_evaluation():
    from utils.evaluation_runner import run_evaluation
    await run_evaluation(top_n=10)
    return {"message": "Evaluation completed"}