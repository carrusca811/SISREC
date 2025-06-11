import asyncio
import numpy as np
from math import isnan
from bson import ObjectId
from database import reviews_collection, users_collection, movies_collection
from utils.colaborative_filtering_utils import build_user_movie_matrix, recommend_movies_for_user
from utils.content_based_utils import get_content_based_recommendations
from utils.evaluation import evaluate_classification, evaluate_predictions

def print_evaluation_summary(results):
    print("\n" + "="*80)
    print("🎯 RESUMO DA AVALIAÇÃO DO SISTEMA DE RECOMENDAÇÃO")
    print("="*80)
    print(f"{'Método':<16}{'Precision':<10}{'Recall':<10}{'F1-Score':<10}{'Accuracy':<10}{'RankScore':<12}{'MAE':<10}{'RMSE':<10}{'RMAE':<10}")
    print("-"*80)
    for method, metrics in results.items():
        print(f"{method:<16}{metrics['precision']:<10.4f}{metrics['recall']:<10.4f}{metrics['f1_score']:<10.4f}{metrics['accuracy']:<10.4f}{metrics['rank_score']:<12.4f}{metrics['mae']:<10.4f}{metrics['rmse']:<10.4f}{metrics['rmae']:<10.4f}")
    print("="*80)

    print("\n🏆 MELHORES RESULTADOS:")
    print(f"   Precision: {max(results.items(), key=lambda x: x[1]['precision'])[0]} ({max(r['precision'] for r in results.values()):.4f})")
    print(f"   Recall: {max(results.items(), key=lambda x: x[1]['recall'])[0]} ({max(r['recall'] for r in results.values()):.4f})")
    print(f"   F1-Score: {max(results.items(), key=lambda x: x[1]['f1_score'])[0]} ({max(r['f1_score'] for r in results.values()):.4f})")
    print("="*80)


async def run_evaluation(top_n=10):
    print("🚀 Iniciando avaliação completa...")

    users = await users_collection.find().to_list(None)
    reviews = await reviews_collection.find().to_list(None)

    print(f"📊 Dados carregados: {len(users)} utilizadores, {len(reviews)} reviews")

    ratings_map = {}
    for r in reviews:
        uid = str(r["user_id"])
        mid = str(r["movie_id"])
        rating = float(r["rating"])
        ratings_map.setdefault(uid, {})[mid] = rating

    print(f"🎯 Utilizadores com reviews: {len(ratings_map)}")

    valid_users = [u for u in users if len(ratings_map.get(str(u["_id"]), {})) >= 5]
    print(f"✅ Utilizadores válidos (≥5 reviews): {len(valid_users)}")

    if len(valid_users) == 0:
        print("❌ Nenhum utilizador com reviews suficientes para avaliação")
        return

    # CONTENT-BASED
    print("\n🎬 Avaliando Content-Based...")
    cb_results, cb_processed, cb_true, cb_pred = [], 0, [], []
    for user in valid_users:
        uid = str(user["_id"])
        rated_movies = ratings_map.get(uid, {})
        try:
            movie_ids = list(rated_movies.keys())
            np.random.shuffle(movie_ids)
            split_point = int(len(movie_ids) * 0.8)
            train_ids, test_ids = set(movie_ids[:split_point]), set(movie_ids[split_point:])
            if len(test_ids) == 0:
                continue

            test_reviews = []
            for mid in test_ids:
                test_reviews.append({"user_id": ObjectId(uid), "movie_id": ObjectId(mid)})
                await reviews_collection.delete_one({"user_id": ObjectId(uid), "movie_id": ObjectId(mid)})

            cb_recs = await get_content_based_recommendations(uid)

            for review_data in test_reviews:
                await reviews_collection.insert_one({
                    **review_data,
                    "rating": rated_movies[str(review_data["movie_id"])]
                })

            if cb_recs:
                recommended_ids = []
                for group in cb_recs:
                    for movie in group.get("top_movies", []):
                        mid = str(movie.get("id", movie.get("_id", "")))
                        if mid and mid not in train_ids:
                            recommended_ids.append(mid)

                relevant_ids = [mid for mid in test_ids if rated_movies[mid] >= 4.0]
                cb_true.extend([rated_movies[mid] for mid in test_ids])
                cb_pred.extend([rated_movies.get(mid, 0) for mid in test_ids])

                if recommended_ids and relevant_ids:
                    cb_results.append((uid, recommended_ids[:top_n], relevant_ids))
                    cb_processed += 1
        except Exception as e:
            print(f"❌ Erro CB para user {uid}: {e}")
    print(f"✅ Content-Based processado: {cb_processed} utilizadores")

    # COLLABORATIVE
    print("\n🤝 Avaliando Collaborative Filtering...")
    cf_results, cf_processed, cf_true, cf_pred = [], 0, [], []
    try:
        matrix = await build_user_movie_matrix()
        print(f"📊 Matriz construída: {matrix.shape}")
        for user in valid_users:
            uid = str(user["_id"])
            if uid not in matrix.index:
                continue
            rated_movies = ratings_map.get(uid, {})
            movie_ids = list(rated_movies.keys())
            np.random.shuffle(movie_ids)
            split_point = int(len(movie_ids) * 0.8)
            train_ids, test_ids = set(movie_ids[:split_point]), set(movie_ids[split_point:])
            if len(test_ids) == 0:
                continue
            train_matrix = matrix.copy()
            for mid in test_ids:
                if mid in train_matrix.columns:
                    train_matrix.loc[uid, mid] = np.nan
            recommended_ids = recommend_movies_for_user(train_matrix, uid, top_n=top_n*2)
            filtered_recs = [mid for mid in recommended_ids if mid not in train_ids]
            relevant_ids = [mid for mid in test_ids if rated_movies[mid] >= 4.0]
            cf_true.extend([rated_movies[mid] for mid in test_ids])
            cf_pred.extend([rated_movies.get(mid, 0) for mid in test_ids])
            if filtered_recs and relevant_ids:
                cf_results.append((uid, filtered_recs[:top_n], relevant_ids))
                cf_processed += 1
    except Exception as e:
        print(f"❌ Erro CF: {e}")
    print(f"✅ Collaborative Filtering processado: {cf_processed} utilizadores")

    # HYBRID
    print("\n⚡ Avaliando Hybrid...")
    hybrid_results, hybrid_processed, hy_true, hy_pred = [], 0, [], []
    for user in valid_users:
        uid = str(user["_id"])
        rated_movies = ratings_map.get(uid, {})
        try:
            movie_ids = list(rated_movies.keys())
            np.random.shuffle(movie_ids)
            split_point = int(len(movie_ids) * 0.8)
            train_ids, test_ids = set(movie_ids[:split_point]), set(movie_ids[split_point:])
            if len(test_ids) == 0:
                continue
            test_reviews = []
            for mid in test_ids:
                test_reviews.append({"user_id": ObjectId(uid), "movie_id": ObjectId(mid)})
                await reviews_collection.delete_one({"user_id": ObjectId(uid), "movie_id": ObjectId(mid)})
            cb_recs = await get_content_based_recommendations(uid)
            cb_ids = set()
            if cb_recs:
                for group in cb_recs:
                    for movie in group.get("top_movies", []):
                        mid = str(movie.get("id", movie.get("_id", "")))
                        if mid and mid not in train_ids:
                            cb_ids.add(mid)
            for review_data in test_reviews:
                await reviews_collection.insert_one({
                    **review_data,
                    "rating": rated_movies[str(review_data["movie_id"])]
                })
            if uid in matrix.index:
                train_matrix = matrix.copy()
                for mid in test_ids:
                    if mid in train_matrix.columns:
                        train_matrix.loc[uid, mid] = np.nan
                cf_ids = set(recommend_movies_for_user(train_matrix, uid, top_n=top_n*2))
                cf_ids = {mid for mid in cf_ids if mid not in train_ids}
            else:
                cf_ids = set()
            combined_ids = list((cb_ids | cf_ids))
            relevant_ids = [mid for mid in test_ids if rated_movies[mid] >= 4.0]
            hy_true.extend([rated_movies[mid] for mid in test_ids])
            hy_pred.extend([rated_movies.get(mid, 0) for mid in test_ids])
            if combined_ids and relevant_ids:
                hybrid_results.append((uid, combined_ids[:top_n], relevant_ids))
                hybrid_processed += 1
        except Exception as e:
            print(f"❌ Erro Hybrid para user {uid}: {e}")
    print(f"✅ Hybrid processado: {hybrid_processed} utilizadores")

    print("\n📊 Calculando métricas...")
    
    results = {
        "Content-Based": evaluate_classification(cb_results, top_k=top_n),
        "Collaborative": evaluate_classification(cf_results, top_k=top_n),
        "Hybrid": evaluate_classification(hybrid_results, top_k=top_n)
    }


    print_evaluation_summary(results)

    print("\n📋 Avaliação individual por utilizador:")
    for uid, recommendations, relevant in cb_results:
        inter = set(recommendations) & set(relevant)
        print(f"[CB] user={uid} → Recs: {len(recommendations)}, Relevant: {len(relevant)}, Matches: {len(inter)}")
    for uid, recommendations, relevant in cf_results:
        inter = set(recommendations) & set(relevant)
        print(f"[CF] user={uid} → Recs: {len(recommendations)}, Relevant: {len(relevant)}, Matches: {len(inter)}")
    for uid, recommendations, relevant in hybrid_results:
        inter = set(recommendations) & set(relevant)
        print(f"[HY] user={uid} → Recs: {len(recommendations)}, Relevant: {len(relevant)}, Matches: {len(inter)}")

    return results
