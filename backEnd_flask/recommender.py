from bson import ObjectId
from sklearn.metrics.pairwise import cosine_similarity
from utils.cold_start_utils import cold_start_user, cold_start_item
import pandas as pd

def generate_recommendations(user_preferences, dataset):
    # Simulação de um dataset
    data = pd.DataFrame(dataset)

    # Calcula a similaridade
    similarity = cosine_similarity([user_preferences], data.drop("item", axis=1))

    # Associa a similaridade com os itens
    data["similarity"] = similarity[0]

    # Ordena pelos mais similares
    recommendations = data.sort_values("similarity", ascending=False).head(5)["item"].tolist()

    return recommendations




def recommend_movies(user_id, movie_id=None):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return cold_start_user(user)

    if movie_id:
        return cold_start_item(movie_id)

    # Continue with collaborative filtering or content-based if user data exists
    #return collaborative_recommendation(user)
