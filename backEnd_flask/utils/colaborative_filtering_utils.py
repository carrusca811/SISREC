from database import reviews_collection
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# --- STEP 1: Criar matriz utilizador-filme
async def build_user_movie_matrix():
    reviews = await reviews_collection.find().to_list(None)

    data = [{
        "user_id": str(r["user_id"]),
        "movie_id": str(r["movie_id"]),
        "rating": r["rating"]
    } for r in reviews]

    df = pd.DataFrame(data)
    user_movie_matrix = df.pivot_table(index="user_id", columns="movie_id", values="rating")
    return user_movie_matrix


# --- STEP 2: Similaridade ajustada com shrinkage e interseção mínima
def adjusted_cosine_similarity(u1, u2, shrinkage=10, min_common_items=5):
    common = (~np.isnan(u1)) & (~np.isnan(u2))
    n_common = np.sum(common)
    if n_common < min_common_items:
        return 0
    sim = cosine_similarity([u1[common]], [u2[common]])[0][0]
    return sim * (n_common / (n_common + shrinkage))


# --- STEP 3: Recomendação de filmes personalizada
def recommend_movies_for_user(matrix: pd.DataFrame, target_user: str, top_n: int = 10, top_k_neighbors: int = 20):
    if target_user not in matrix.index:
        return []

    # Z-score normalization
    user_means = matrix.mean(axis=1)
    user_stds = matrix.std(axis=1).replace(0, 1)
    matrix_zscore = (matrix.sub(user_means, axis=0)).div(user_stds, axis=0)

    # Calcular similaridade com shrinkage e filtrar vizinhos úteis
    similarities = {}
    for user_id in matrix.index:
        if user_id == target_user:
            continue
        sim = adjusted_cosine_similarity(matrix_zscore.loc[target_user], matrix_zscore.loc[user_id])
        if sim > 0.05:  # filtra ruído de similaridade fraca
            similarities[user_id] = sim

    if not similarities:
        # fallback: recomendar os filmes mais populares globalmente
        popular_movies = matrix.notna().sum().sort_values(ascending=False).head(top_n).index.tolist()
        return popular_movies

    # Selecionar os K vizinhos mais parecidos
    top_sim_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k_neighbors]

    weighted_sum = np.zeros(matrix.shape[1])
    sim_sum = np.zeros(matrix.shape[1])

    for sim_user, sim_score in top_sim_users:
        ratings = matrix_zscore.loc[sim_user]
        for movie_id, zscore_rating in ratings.items():
            if not np.isnan(zscore_rating):
                col_idx = matrix.columns.get_loc(movie_id)
                weighted_sum[col_idx] += zscore_rating * sim_score
                sim_sum[col_idx] += abs(sim_score)

    predicted_zscores = np.divide(weighted_sum, sim_sum, out=np.zeros_like(weighted_sum), where=sim_sum != 0)
    predicted_ratings = predicted_zscores * user_stds[target_user] + user_means[target_user]

    # Penalização por popularidade para promover diversidade
    popularity = matrix.notna().sum(axis=0)
    penalty = np.log1p(popularity)
    predicted_ratings -= 0.03 * penalty.values  # peso ajustável

    # Remover filmes já vistos
    watched_movies = matrix.loc[target_user].dropna().index
    predictions = {
        movie_id: predicted_ratings[matrix.columns.get_loc(movie_id)]
        for movie_id in matrix.columns if movie_id not in watched_movies
    }

    # Ordenar e devolver recomendações
    top_recommendations = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [movie_id for movie_id, _ in top_recommendations]
