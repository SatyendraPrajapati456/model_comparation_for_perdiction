"""
Model Evaluation Module for House Price Prediction System.
Calculates MAE, RMSE, and R2 score, formats comparison tables,
and generates performance visual artifacts.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def calculate_metrics(y_true, y_pred) -> dict:
    """
    Computes MAE, RMSE, and R2 score.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4),
        "MAPE": round(mape, 2)
    }


def compare_models(models_dict: dict, X_test, y_test) -> pd.DataFrame:
    """
    Evaluates multiple fitted models on the test set and returns a comparison DataFrame.
    """
    results = []
    for model_name, model in models_dict.items():
        preds = model.predict(X_test)
        metrics = calculate_metrics(y_test, preds)
        results.append({
            "Model": model_name,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "R2 Score": metrics["R2"],
            "MAPE (%)": metrics["MAPE"]
        })

    df_results = pd.DataFrame(results).sort_values(by="R2 Score", ascending=False).reset_index(drop=True)
    return df_results


def plot_model_comparison(comparison_df: pd.DataFrame, output_path: str = "models/model_comparison.png"):
    """
    Generates and saves a bar chart comparing model R2 scores and RMSE.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # R2 Comparison
    sns.barplot(data=comparison_df, x="R2 Score", y="Model", hue="Model", ax=axes[0], palette="Blues_r", legend=False)
    axes[0].set_title("Model Comparison - R2 Score (Higher is Better)")
    axes[0].set_xlim(0, 1)
    for p in axes[0].patches:
        width = p.get_width()
        axes[0].annotate(f'{width:.3f}', (width + 0.02, p.get_y() + p.get_height() / 2.),
                         ha='left', va='center', fontsize=9)

    # RMSE Comparison
    sns.barplot(data=comparison_df, x="RMSE", y="Model", hue="Model", ax=axes[1], palette="Reds_r", legend=False)
    axes[1].set_title("Model Comparison - RMSE (Lower is Better)")
    for p in axes[1].patches:
        width = p.get_width()
        axes[1].annotate(f'Rs. {int(width):,}', (width * 0.05, p.get_y() + p.get_height() / 2.),
                         ha='left', va='center', fontsize=9, color='white', weight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_actual_vs_predicted(y_true, y_pred, model_name: str = "XGBoost", output_path: str = "models/actual_vs_predicted.png"):
    """
    Generates actual vs predicted price scatter plot.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(7, 6))
    plt.scatter(y_true, y_pred, alpha=0.6, edgecolors='b', color='#3b82f6')
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label="Ideal 45° Line")
    plt.xlabel("Actual Price (₹)")
    plt.ylabel("Predicted Price (₹)")
    plt.title(f"{model_name}: Actual vs Predicted House Prices")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_metrics_json(comparison_df: pd.DataFrame, best_params: dict, output_path: str = "models/model_metrics.json"):
    """
    Saves metrics summary and tuning parameters to JSON.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = {
        "comparison": comparison_df.to_dict(orient="records"),
        "best_xgboost_params": best_params,
        "selected_production_model": "Tuned XGBoost Regressor"
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
