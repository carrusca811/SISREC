import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Dict, List, Tuple, Callable

# Função auxiliar: split train/test

def split_train_test(user_movie_matrix: pd.DataFrame, test_ratio=0.2) -> Tuple[pd.DataFrame, Dict[str, set]]:
    train = user_movie_matrix.copy()
    test = {}

    for user in user_movie_matrix.index:
        seen = user_movie_matrix.loc[user].dropna()
        if len(seen) < 5:
            continue
        test_items = seen.sample(frac=test_ratio)
        train.loc[user, test_items.index] = np.nan
        test[user] = set(test_items.index)

    return train, test

# Avalia recomendações dadas por uma função de recomendador

def evaluate_model(
    user_ids: List[str],
    recommend_fn: Callable[[str, int], List],
    test_data: Dict[str, set],
    top_n: int = 10
) -> Dict[str, float]:

    precision_list, recall_list = [], []
    hit_count = 0
    total_users = 0

    for user_id in tqdm(user_ids):
        if user_id not in test_data:
            continue

        test_items = test_data[user_id]
        try:
            recs = recommend_fn(user_id, top_n)
            if not recs:
                continue

            if isinstance(recs[0], tuple):  # ALS (id, score) ou outros
                recs = [r[0] for r in recs]

            hits = set(recs).intersection(test_items)
            hit_count += 1 if hits else 0

            precision = len(hits) / top_n
            recall = len(hits) / len(test_items)

            precision_list.append(precision)
            recall_list.append(recall)
            total_users += 1
        except Exception as e:
            print(f"Erro no utilizador {user_id}: {e}")
            continue

    return {
        "Precision@{}".format(top_n): round(np.mean(precision_list), 4) if precision_list else 0.0,
        "Recall@{}".format(top_n): round(np.mean(recall_list), 4) if recall_list else 0.0,
        "HitRate": round(hit_count / total_users, 4) if total_users > 0 else 0.0
    }

# Exemplo de uso:
# - definir recommend_fn para cada abordagem (ALS, CB, Hybrid, Cold Start)
# - chamar evaluate_model com a lista de user_ids e test_data
# - comparar os resultados
