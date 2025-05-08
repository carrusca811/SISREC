from sklearn.metrics.pairwise import cosine_similarity
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
