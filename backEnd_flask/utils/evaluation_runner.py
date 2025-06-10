
import asyncio
from utils.evaluation_pipelyne import split_train_test, evaluate_model
from utils.colaborative_als import build_als_training_data, build_als_model, recommend_movies_als
from utils.content_based_utils import get_content_based_recommendations
from utils.cold_start_utils import cold_start_python_filter

from utils.colaborative_filtering_utils import recommend_movies_for_user, build_user_movie_matrix

async def run_evaluation(top_n=10):
    print("\n🔍 Iniciando avaliação dos sistemas de recomendação...")

    # --- MATRIZ COMPLETA
    df_als, full_matrix = await build_als_training_data()
    train_matrix, test_data = split_train_test(full_matrix, test_ratio=0.2)
    user_ids = list(test_data.keys())

    # --- ALS
    print("\n✅ Avaliando ALS...")
    model, uid_map, mid_rev_map, als_matrix = build_als_model(df_als, train_matrix)
    def als_fn(user_id, top_n):
        return recommend_movies_als(model, als_matrix, uid_map, mid_rev_map, user_id, top_n)
    als_results = evaluate_model(user_ids, als_fn, test_data, top_n=top_n)

    # --- Content-Based
    print("\n✅ Avaliando Content-Based...")
    async def cb_fn(user_id, top_n):
        result = await get_content_based_recommendations(user_id)
        flat = [m for g in result for m in g["top_movies"]]
        return [(m["id"], 1.0) for m in flat[:top_n]]
    cb_results = await evaluate_model_async(user_ids, cb_fn, test_data, top_n=top_n)

    # --- Cold Start
    print("\n✅ Avaliando Cold Start...")
    async def cs_fn(user_id, top_n):
        result = await cold_start_python_filter(user_id)
        return [(m["id"], 1.0) for m in result[:top_n]]
    cs_results = await evaluate_model_async(user_ids, cs_fn, test_data, top_n=top_n)

    # --- Collaborative Filtering (Tradicional)
    print("\n✅ Avaliando CF Similaridade...")
    matrix_cf = await build_user_movie_matrix()
    def cf_fn(user_id, top_n):
        return [(m, 1.0) for m in recommend_movies_for_user(matrix_cf, user_id, top_n)]
    cf_results = evaluate_model(user_ids, cf_fn, test_data, top_n=top_n)

    # --- Resultados
    print("\n📊 Resultados Finais:")
    for name, metrics in zip(["ALS", "Content-Based", "Cold Start", "CF Similaridade"],
                              [als_results, cb_results, cs_results, cf_results]):
        print(f"\n🔸 {name}:")
        for k, v in metrics.items():
            print(f"{k}: {v}")

# Avaliação assíncrona
async def evaluate_model_async(user_ids, async_fn, test_data, top_n):
    results = []
    for uid in user_ids:
        if uid not in test_data:
            continue
        try:
            recs = await async_fn(uid, top_n)
            recs = [r[0] for r in recs] if recs and isinstance(recs[0], tuple) else recs
            hits = set(recs).intersection(test_data[uid])
            precision = len(hits) / top_n
            recall = len(hits) / len(test_data[uid])
            results.append((precision, recall, 1 if hits else 0))
        except:
            continue

    precisions = [r[0] for r in results]
    recalls = [r[1] for r in results]
    hits = [r[2] for r in results]

    return {
        f"Precision@{top_n}": round(sum(precisions) / len(precisions), 4) if precisions else 0.0,
        f"Recall@{top_n}": round(sum(recalls) / len(recalls), 4) if recalls else 0.0,
        "HitRate": round(sum(hits) / len(hits), 4) if hits else 0.0
    }

if __name__ == "__main__":
    asyncio.run(run_evaluation())
