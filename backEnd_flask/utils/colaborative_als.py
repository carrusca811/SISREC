from database import reviews_collection
from implicit.als import AlternatingLeastSquares
from scipy.sparse import coo_matrix
import pandas as pd
import numpy as np

# Cache global para evitar retrain constante
ALS_MODEL_CACHE = {
    "model": None,
    "matrix": None,
    "user_id_map": None,
    "movie_id_reverse_map": None,
    "data_hash": None
}

# --- STEP 1: Criar matriz user-movie a partir do MongoDB
async def build_als_training_data():
    reviews = await reviews_collection.find().to_list(None)

    data = [
        {
            "user_id": str(r["user_id"]),
            "movie_id": str(r["movie_id"]),
            "rating": float(r["rating"])
        } for r in reviews
    ]

    df = pd.DataFrame(data)

    # Normalização: mean-centering por utilizador
    df["rating"] = df.groupby("user_id")["rating"].transform(lambda x: x - x.mean())

    user_movie_matrix = df.pivot_table(index="user_id", columns="movie_id", values="rating")
    return df, user_movie_matrix

# --- STEP 2: Treinar modelo ALS com biblioteca implicit
def build_als_model(df: pd.DataFrame, user_movie_matrix: pd.DataFrame, factors=50, regularization=0.01, iterations=15):
    import hashlib
    current_hash = hashlib.sha1(df.to_csv(index=False).encode()).hexdigest()

    if ALS_MODEL_CACHE["data_hash"] == current_hash:
        return ALS_MODEL_CACHE["model"], ALS_MODEL_CACHE["user_id_map"], ALS_MODEL_CACHE["movie_id_reverse_map"], ALS_MODEL_CACHE["matrix"]

    user_ids = list(user_movie_matrix.index)
    movie_ids = list(user_movie_matrix.columns)

    user_id_map = {uid: i for i, uid in enumerate(user_ids)}
    movie_id_map = {mid: i for i, mid in enumerate(movie_ids)}
    movie_id_reverse_map = {i: mid for mid, i in movie_id_map.items()}

    rows, cols, data_vals = [], [], []
    for _, row in df.iterrows():
        uid = user_id_map.get(row["user_id"])
        mid = movie_id_map.get(row["movie_id"])
        if uid is not None and mid is not None:
            rows.append(uid)
            cols.append(mid)
            data_vals.append(row["rating"])

    from scipy.sparse import csr_matrix
    matrix = csr_matrix((data_vals, (rows, cols)), shape=(len(user_ids), len(movie_ids)))

    model = AlternatingLeastSquares(factors=factors, regularization=regularization, iterations=iterations)
    model.fit(matrix)

    ALS_MODEL_CACHE.update({
        "model": model,
        "user_id_map": user_id_map,
        "movie_id_reverse_map": movie_id_reverse_map,
        "matrix": matrix,
        "data_hash": current_hash
    })

    return model, user_id_map, movie_id_reverse_map, matrix

# --- STEP 3: Gerar recomendações para um utilizador

def recommend_movies_als(model, matrix, user_id_map, movie_id_reverse_map, target_user_id: str, top_n=10):
    if target_user_id not in user_id_map:
        # fallback para filmes populares
        popular_movies = np.array(matrix.sum(axis=0)).flatten()
        top_indices = np.argsort(-popular_movies)[:top_n]
        return [(movie_id_reverse_map.get(i), float(popular_movies[i])) for i in top_indices]

    user_idx = user_id_map[target_user_id]
    user_items = matrix[user_idx]

    recs = model.recommend(user_idx, user_items, N=top_n, filter_already_liked_items=True)

    # Penalização por popularidade
    movie_popularity = np.array(matrix.sum(axis=0)).flatten()
    penalty = np.log1p(movie_popularity)

    penalty = np.log1p(movie_popularity)
    adjusted_scores = [
    (movie_id_reverse_map.get(i), float(score - 0.03 * penalty[i]))
    for i, score in zip(recs[0], recs[1])
    ]
    # Ordenar novamente após penalização
    adjusted_scores.sort(key=lambda x: x[1], reverse=True)
    return adjusted_scores[:top_n]