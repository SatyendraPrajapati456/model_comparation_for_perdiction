"""
Power BI Data Preparation & Export Script.
Generates structured CSV datasets and DAX formulas for Microsoft Power BI dashboards:
  - Dashboard 1: Housing Overview
  - Dashboard 2: Price Analysis
  - Dashboard 3: Prediction Analytics
  - Dashboard 4: Model Performance
"""

import os
import json
import pandas as pd
import numpy as np


def prepare_powerbi_datasets():
    output_dir = os.path.dirname(__file__)
    data_path = os.path.join(output_dir, "..", "data", "house_data.csv")
    metrics_path = os.path.join(output_dir, "..", "models", "model_metrics.json")

    # 1. Housing Overview & Price Analysis Dataset
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        # Add Power BI friendly calculated columns
        df['total_rooms'] = df['bedrooms'] + df['bathrooms']
        df['area_per_room'] = (df['area'] / df['total_rooms'].replace(0, 1)).round(1)
        df['bathroom_per_bedroom'] = (df['bathrooms'] / df['bedrooms'].replace(0, 1)).round(2)
        df['price_per_sqft'] = (df['price'] / df['area']).round(2)
        
        # Price Brackets for segmentation
        bins = [0, 3000000, 5000000, 8000000, 15000000]
        labels = ['< 30 Lakhs', '30L - 50 Lakhs', '50L - 80 Lakhs', '> 80 Lakhs']
        df['price_bracket'] = pd.cut(df['price'], bins=bins, labels=labels)
        
        export_path = os.path.join(output_dir, "powerbi_housing_data.csv")
        df.to_csv(export_path, index=False)
        print(f"Generated Power BI Housing Data: {export_path} ({len(df)} rows)")

    # 2. Model Performance Dataset
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            comparison = data.get("comparison", [])
            df_perf = pd.DataFrame(comparison)
            perf_path = os.path.join(output_dir, "powerbi_model_performance.csv")
            df_perf.to_csv(perf_path, index=False)
            print(f"Generated Power BI Model Performance: {perf_path}")

    # 3. Prediction Analytics Sample Dataset
    # Provide initial sample log if DB is newly initialized
    pred_path = os.path.join(output_dir, "powerbi_prediction_history.csv")
    sample_preds = [
        {"prediction_id": 1, "area": 7420, "bedrooms": 4, "bathrooms": 2, "stories": 3, "parking": 2, "mainroad": "yes", "airconditioning": "yes", "prefarea": "yes", "furnishingstatus": "furnished", "predicted_price": 9830081.0, "timestamp": "2026-09-26 01:10:00"},
        {"prediction_id": 2, "area": 8960, "bedrooms": 4, "bathrooms": 4, "stories": 4, "parking": 3, "mainroad": "yes", "airconditioning": "yes", "prefarea": "no", "furnishingstatus": "furnished", "predicted_price": 11450000.0, "timestamp": "2026-09-26 01:12:00"},
        {"prediction_id": 3, "area": 4600, "bedrooms": 3, "bathrooms": 1, "stories": 2, "parking": 1, "mainroad": "yes", "airconditioning": "yes", "prefarea": "no", "furnishingstatus": "semi-furnished", "predicted_price": 4950000.0, "timestamp": "2026-09-26 01:14:00"},
        {"prediction_id": 4, "area": 2500, "bedrooms": 2, "bathrooms": 1, "stories": 1, "parking": 0, "mainroad": "yes", "airconditioning": "no", "prefarea": "no", "furnishingstatus": "unfurnished", "predicted_price": 2850000.0, "timestamp": "2026-09-26 01:16:00"},
        {"prediction_id": 5, "area": 6000, "bedrooms": 3, "bathrooms": 2, "stories": 2, "parking": 2, "mainroad": "yes", "airconditioning": "yes", "prefarea": "yes", "furnishingstatus": "semi-furnished", "predicted_price": 6800000.0, "timestamp": "2026-09-26 01:18:00"},
        {"prediction_id": 6, "area": 5500, "bedrooms": 4, "bathrooms": 2, "stories": 2, "parking": 1, "mainroad": "no", "airconditioning": "yes", "prefarea": "no", "furnishingstatus": "furnished", "predicted_price": 5750000.0, "timestamp": "2026-09-26 01:20:00"},
        {"prediction_id": 7, "area": 3800, "bedrooms": 3, "bathrooms": 1, "stories": 1, "parking": 1, "mainroad": "yes", "airconditioning": "no", "prefarea": "no", "furnishingstatus": "unfurnished", "predicted_price": 3650000.0, "timestamp": "2026-09-26 01:22:00"}
    ]
    pd.DataFrame(sample_preds).to_csv(pred_path, index=False)
    print(f"Generated Power BI Prediction History: {pred_path}")


if __name__ == "__main__":
    prepare_powerbi_datasets()
