from database import reviews_collection
import pandas as pd
import numpy as np

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

# --- STEP 2: Pearson Correlation com ajuste e mínimo de itens em comum
def pearson_similarity(u1, u2, min_common_items=5):
    common = (~np.isnan(u1)) & (~np.isnan(u2))
    if np.sum(common) < min_common_items:
        return 0
    
    u1_common = u1[common]
    u2_common = u2[common]
    u1_mean = np.nanmean(u1_common)
    u2_mean = np.nanmean(u2_common)

    numerator = np.sum((u1_common - u1_mean) * (u2_common - u2_mean))
    denominator = np.sqrt(np.sum((u1_common - u1_mean) ** 2)) * np.sqrt(np.sum((u2_common - u2_mean) ** 2))
    
    if denominator == 0:
        return 0
    
    return numerator / denominator

# --- STEP 3: Previsão com base nos vizinhos mais semelhantes
def recommend_movies_for_user(matrix: pd.DataFrame, target_user: str, top_n: int = 10, top_k_neighbors: int = 20):
    if target_user not in matrix.index:
        return []

    similarities = {}
    for user_id in matrix.index:
        if user_id == target_user:
            continue
        sim = pearson_similarity(matrix.loc[target_user], matrix.loc[user_id])
        if sim > 0.05:
            similarities[user_id] = sim

    if not similarities:
        # fallback: filmes mais populares
        popular_movies = matrix.notna().sum().sort_values(ascending=False).head(top_n).index.tolist()
        return popular_movies

    top_neighbors = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k_neighbors]

    target_mean = matrix.loc[target_user].mean()
    predictions = {}

    for movie_id in matrix.columns:
        if not np.isnan(matrix.loc[target_user, movie_id]):
            continue

        num, denom = 0, 0
        for neighbor, sim in top_neighbors:
            neighbor_rating = matrix.loc[neighbor, movie_id]
            if not np.isnan(neighbor_rating):
                neighbor_mean = matrix.loc[neighbor].mean()
                num += sim * (neighbor_rating - neighbor_mean)
                denom += abs(sim)

        if denom > 0:
            predictions[movie_id] = target_mean + num / denom

    recommended = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [movie_id for movie_id, _ in recommended]