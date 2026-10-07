"""
Training & Model Optimization Module for House Price Prediction System.
Trains 5 candidate models, performs 5-fold cross-validated hyperparameter tuning
for XGBoost Regressor, compares performance, and saves the final model to models/model.pkl.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor

from src.preprocessing import (
    prepare_train_test_data,
    create_full_pipeline,
    clean_dataset,
    load_dataset
)
from src.evaluate import (
    compare_models,
    plot_model_comparison,
    plot_actual_vs_predicted,
    save_metrics_json,
    calculate_metrics
)


def train_and_evaluate_all():
    print("=" * 60)
    print("Starting End-to-End House Price Prediction Training Pipeline")
    print("=" * 60)

    # 1. Load and split data
    print("\n[Step 1/5] Loading and Splitting Data...")
    X_train, X_test, y_train, y_test = prepare_train_test_data(
        file_path="data/house_data.csv",
        test_size=0.2,
        random_state=42
    )
    print(f"  Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    # 2. Define baseline models
    print("\n[Step 2/5] Training Baseline Models...")
    candidate_regressors = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "XGBoost (Baseline)": XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42
        )
    }

    fitted_pipelines = {}
    for name, reg in candidate_regressors.items():
        print(f"  Fitting {name}...")
        pipeline = create_full_pipeline(reg)
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline

    # 3. XGBoost Hyperparameter Tuning
    print("\n[Step 3/5] Hyperparameter Tuning for XGBoost via 5-Fold Cross Validation...")
    # Base pipeline template for tuning
    tuning_pipeline = create_full_pipeline(
        XGBRegressor(objective="reg:squarederror", random_state=42)
    )

    param_grid = {
        'regressor__n_estimators': [100, 150, 200],
        'regressor__learning_rate': [0.03, 0.05, 0.08],
        'regressor__max_depth': [2, 3, 4],
        'regressor__subsample': [0.8, 1.0],
        'regressor__colsample_bytree': [0.8, 1.0],
        'regressor__reg_alpha': [0.1, 1.0],
        'regressor__reg_lambda': [1.0, 2.0]
    }

    grid_search = GridSearchCV(
        estimator=tuning_pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)

    best_pipeline = grid_search.best_estimator_
    best_params = {k.replace('regressor__', ''): v for k, v in grid_search.best_params_.items()}
    print(f"  Best Cross-Validated Hyperparameters: {best_params}")
    fitted_pipelines["XGBoost (Tuned)"] = best_pipeline

    # 4. Model Comparison & Evaluation
    print("\n[Step 4/5] Evaluating and Comparing All Models on Held-Out Test Set...")
    comparison_df = compare_models(fitted_pipelines, X_test, y_test)
    print("\n" + "=" * 70)
    print("                     MODEL PERFORMANCE COMPARISON")
    print("=" * 70)
    print(comparison_df.to_string(index=False))
    print("=" * 70)

    # Generate visual artifacts
    os.makedirs("models", exist_ok=True)
    os.makedirs("powerbi", exist_ok=True)
    plot_model_comparison(comparison_df, "models/model_comparison.png")

    y_test_pred = best_pipeline.predict(X_test)
    plot_actual_vs_predicted(y_test, y_test_pred, model_name="Tuned XGBoost", output_path="models/actual_vs_predicted.png")
    save_metrics_json(comparison_df, best_params, "models/model_metrics.json")

    # Export comparison to Power BI data directory
    comparison_df.to_csv("powerbi/powerbi_model_performance.csv", index=False)

    # 5. Saving Final Model
    print("\n[Step 5/5] Saving Final Tuned Pipeline as models/model.pkl...")
    model_output_path = "models/model.pkl"
    joblib.dump(best_pipeline, model_output_path)
    print(f"  Final model saved successfully to: {os.path.abspath(model_output_path)}")

    final_metrics = calculate_metrics(y_test, y_test_pred)
    print(f"\nFinal Production Model (Tuned XGBoost) Test Metrics:")
    print(f"  - MAE:      INR {final_metrics['MAE']:,.2f}")
    print(f"  - RMSE:     INR {final_metrics['RMSE']:,.2f}")
    print(f"  - R2 Score: {final_metrics['R2']:.4f}")
    print(f"  - MAPE:     {final_metrics['MAPE']:.2f}%")

    return best_pipeline, comparison_df


if __name__ == "__main__":
    train_and_evaluate_all()
