import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import List, Tuple, Dict

def evaluate_predictions(true_ratings: List[float], predicted_ratings: List[float]) -> Dict[str, float]:
    if not true_ratings or not predicted_ratings or len(true_ratings) != len(predicted_ratings):
        return {"mae": 0.0, "rmse": 0.0, "rmae": 0.0, "accuracy": 0.0}

    mae = mean_absolute_error(true_ratings, predicted_ratings)
    rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))
    rmae = np.sqrt(mae) if mae > 0 else 0.0
    correct = sum(abs(t - p) <= 1 for t, p in zip(true_ratings, predicted_ratings))
    accuracy = correct / len(true_ratings)

    return {
        "mae": mae,
        "rmse": rmse,
        "rmae": rmae,
        "accuracy": accuracy
    }

def evaluate_classification(recommendations: List[Tuple[str, List[str], List[str]]], top_k: int = 10) -> Dict[str, float]:
    if not recommendations:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "rank_score": 0.0,
            "accuracy": 0.0,
            "mae": 0.0,
            "rmse": 0.0,
            "rmae": 0.0
        }

    precisions, recalls, f1s, rank_scores, accuracies = [], [], [], [], []
    true_ratings, predicted_ratings = [], []

    for uid, recommended, relevant in recommendations:
        recommended_top = recommended[:top_k]
        if not relevant:
            continue

        relevant_set = set(relevant)
        recommended_set = set(recommended_top)
        intersection = recommended_set & relevant_set

        tp = len(intersection)
        fp = len(recommended_set) - tp
        fn = len(relevant_set) - tp

        precision = tp / len(recommended_set) if recommended_set else 0.0
        recall = tp / len(relevant_set) if relevant_set else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        acc = tp / len(recommended_top) if recommended_top else 0.0
        rs = rank_score(recommended_top, relevant)

        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        accuracies.append(acc)
        rank_scores.append(rs)

        # Simular previsões como binárias apenas para fins de regressão (não ideal)
        true_ratings.extend([1.0 if mid in relevant_set else 0.0 for mid in recommended_top])
        predicted_ratings.extend([1.0 if mid in recommended_set else 0.0 for mid in recommended_top])

    if true_ratings and predicted_ratings:
        mae = mean_absolute_error(true_ratings, predicted_ratings)
        rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))
        rmae = np.sqrt(mae) if mae > 0 else 0.0
    else:
        mae = rmse = rmae = 0.0

    return {
        "precision": np.mean(precisions),
        "recall": np.mean(recalls),
        "f1_score": np.mean(f1s),
        "rank_score": np.mean(rank_scores),
        "accuracy": np.mean(accuracies),
        "mae": mae,
        "rmse": rmse,
        "rmae": rmae
    }
def rank_score(recommended_list: List[str], relevant_items: List[str], alpha: int = 2) -> float:
    if not recommended_list or not relevant_items:
        return 0.0

    relevant_set = set(relevant_items)
    hits = [i + 1 for i, mid in enumerate(recommended_list) if mid in relevant_set]

    if not hits:
        return 0.0

    score = sum([1 / (2 ** ((pos - 1) / (alpha - 1))) for pos in hits])
    ideal_positions = list(range(1, min(len(relevant_items), len(recommended_list)) + 1))
    ideal_score = sum([1 / (2 ** ((pos - 1) / (alpha - 1))) for pos in ideal_positions])

    return score / ideal_score if ideal_score > 0 else 0.0

def print_evaluation_summary(results: Dict[str, Dict[str, float]]):
    print("\n" + "="*80)
    print("🎯 RESUMO DA AVALIAÇÃO DO SISTEMA DE RECOMENDAÇÃO")
    print("="*80)
    print(f"{'Método':<15} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Accuracy':<10} {'RankScore':<10} {'MAE':<10} {'RMSE':<10} {'RMAE':<10}")
    print("-" * 80)

    for method, metrics in results.items():
        print(f"{method:<15} "
              f"{metrics.get('precision', 0.0):<10.4f} "
              f"{metrics.get('recall', 0.0):<10.4f} "
              f"{metrics.get('f1_score', 0.0):<10.4f} "
              f"{metrics.get('accuracy', 0.0):<10.4f} "
              f"{metrics.get('rank_score', 0.0):<10.4f} "
              f"{metrics.get('mae', 0.0):<10.4f} "
              f"{metrics.get('rmse', 0.0):<10.4f} "
              f"{metrics.get('rmae', 0.0):<10.4f}")

    print("="*80)
    best_precision = max(results.items(), key=lambda x: x[1].get('precision', 0))
    best_recall = max(results.items(), key=lambda x: x[1].get('recall', 0))
    best_f1 = max(results.items(), key=lambda x: x[1].get('f1_score', 0))

    print(f"\n🏆 MELHORES RESULTADOS:")
    print(f"   Precision: {best_precision[0]} ({best_precision[1]['precision']:.4f})")
    print(f"   Recall: {best_recall[0]} ({best_recall[1]['recall']:.4f})")
    print(f"   F1-Score: {best_f1[0]} ({best_f1[1]['f1_score']:.4f})")
    print("="*80)
