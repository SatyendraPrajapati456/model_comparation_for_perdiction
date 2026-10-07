

"""
Data Preprocessing and Feature Engineering Module for House Price Prediction System.
"""

import os
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


# Column categorizations
NUMERICAL_COLS = ['area', 'bedrooms', 'bathrooms', 'stories', 'parking']
BINARY_COLS = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']
CATEGORICAL_COLS = ['furnishingstatus']
TARGET_COL = 'price'

DERIVED_NUMERICAL_COLS = ['total_rooms', 'area_per_room', 'bathroom_per_bedroom']
ALL_NUMERICAL_COLS = NUMERICAL_COLS + DERIVED_NUMERICAL_COLS


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn Transformer for Domain Feature Engineering.
    Computes:
      - total_rooms = bedrooms + bathrooms
      - area_per_room = area / max(total_rooms, 1)
      - bathroom_per_bedroom = bathrooms / max(bedrooms, 1)
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Support both pandas DataFrame and dictionary/numpy structures
        if isinstance(X, pd.DataFrame):
            df = X.copy()
        elif isinstance(X, dict):
            df = pd.DataFrame([X])
        else:
            raise TypeError("Expected pandas DataFrame or dictionary for transform.")

        # Ensure numeric types
        for col in ['area', 'bedrooms', 'bathrooms', 'stories', 'parking']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Feature Engineering (Section 9 of requirements)
        df['total_rooms'] = df['bedrooms'] + df['bathrooms']
        df['area_per_room'] = df['area'] / df['total_rooms'].replace(0, 1)
        df['bathroom_per_bedroom'] = df['bathrooms'] / df['bedrooms'].replace(0, 1)

        # Normalize string values for binary and categorical columns
        for col in BINARY_COLS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
        if 'furnishingstatus' in df.columns:
            df['furnishingstatus'] = df['furnishingstatus'].astype(str).str.strip().str.lower()

        return df


def load_dataset(file_path: str = "data/house_data.csv") -> pd.DataFrame:
    """
    Loads housing dataset from CSV file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    df = pd.read_csv(file_path)
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs data cleaning:
      - Removes duplicates
      - Drops nulls if any
      - Validates data types
    """
    cleaned_df = df.copy()
    cleaned_df.drop_duplicates(inplace=True)
    cleaned_df.dropna(inplace=True)

    # Validate numeric types
    for col in NUMERICAL_COLS + ([TARGET_COL] if TARGET_COL in cleaned_df.columns else []):
        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

    cleaned_df.dropna(inplace=True)
    return cleaned_df


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs the ColumnTransformer for transforming numerical,
    binary, and categorical features.
    """
    num_pipeline = Pipeline([
        ('scaler', StandardScaler())
    ])

    binary_pipeline = Pipeline([
        ('onehot', OneHotEncoder(
            categories=[['no', 'yes']] * len(BINARY_COLS),
            drop='first',
            sparse_output=False,
            handle_unknown='ignore'
        ))
    ])

    categorical_pipeline = Pipeline([
        ('onehot', OneHotEncoder(
            categories=[['furnished', 'semi-furnished', 'unfurnished']],
            drop='first',
            sparse_output=False,
            handle_unknown='ignore'
        ))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, ALL_NUMERICAL_COLS),
            ('bin', binary_pipeline, BINARY_COLS),
            ('cat', categorical_pipeline, CATEGORICAL_COLS)
        ],
        remainder='drop'
    )

    return preprocessor


def create_full_pipeline(regressor) -> Pipeline:
    """
    Creates an end-to-end Pipeline combining Feature Engineering,
    Pre-processing (ColumnTransformer), and the Regression Estimator.
    """
    pipeline = Pipeline([
        ('feature_engineer', FeatureEngineeringTransformer()),
        ('preprocessor', build_preprocessor()),
        ('regressor', regressor)
    ])
    return pipeline


def prepare_train_test_data(file_path: str = "data/house_data.csv", test_size: float = 0.2, random_state: int = 42):
    """
    Loads dataset, cleans it, and splits into train and test sets.
    Returns: X_train, X_test, y_train, y_test
    """
    df = load_dataset(file_path)
    cleaned = clean_dataset(df)

    X = cleaned.drop(columns=[TARGET_COL])
    y = cleaned[TARGET_COL]

    return train_test_split(X, y, test_size=test_size, random_state=random_state)
