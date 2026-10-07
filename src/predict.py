"""
Inference & Prediction Module for House Price Prediction System.
Loads models/model.pkl and performs predictions on input property features.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
from typing import Dict, Any, Union, List
from src.preprocessing import FeatureEngineeringTransformer


MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "model.pkl")

# Cached model instance
_model = None


def format_inr(number: float) -> str:
    """
    Formats a numeric value into the Indian numbering system (e.g. ₹1,05,25,600).
    """
    rounded = int(round(number))
    s = str(rounded)
    if len(s) <= 3:
        return f"₹{s}"
    last_three = s[-3:]
    remaining = s[:-3]
    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        parts.insert(0, remaining)
    return f"₹{','.join(parts)},{last_three}"


def load_model(model_path: str = MODEL_PATH):
    """
    Loads and caches the serialized model pipeline.
    """
    global _model
    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. Please train the model first by running src/train.py"
            )
        _model = joblib.load(model_path)
    return _model


def predict_price(input_data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]) -> List[Dict[str, Any]]:
    """
    Predicts house price given property features.
    
    Accepts:
      - dict of features (single record)
      - list of dicts (batch)
      - pandas DataFrame
      
    Returns:
      List of dicts with predicted_price and formatted_price.
    """
    model = load_model()

    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        df_input = pd.DataFrame(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df_input = input_data.copy()
    else:
        raise ValueError("Unsupported input format. Must be dict, list of dicts, or DataFrame.")

    predictions = model.predict(df_input)

    results = []
    for pred in predictions:
        val = float(pred)
        results.append({
            "predicted_price": round(val, 2),
            "formatted_price": format_inr(val)
        })

    return results


if __name__ == "__main__":
    sample_house = {
        "area": 7420,
        "bedrooms": 4,
        "bathrooms": 2,
        "stories": 3,
        "parking": 2,
        "mainroad": "yes",
        "guestroom": "no",
        "basement": "no",
        "hotwaterheating": "no",
        "airconditioning": "yes",
        "prefarea": "yes",
        "furnishingstatus": "furnished"
    }

    print("Running sample inference test:")
    print("Input:", sample_house)
    prediction = predict_price(sample_house)[0]
    print(f"Predicted Price: {prediction['predicted_price']}")
    try:
        print(f"Formatted: {prediction['formatted_price']}")
    except UnicodeEncodeError:
        print(f"Formatted: Rs. {prediction['predicted_price']:,.2f}")
