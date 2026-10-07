"""
Pydantic Data Validation Schemas for FastAPI House Price Prediction API.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class HouseFeaturesInput(BaseModel):
    area: float = Field(..., ge=100, le=50000, description="Property area in square feet", example=7420)
    bedrooms: int = Field(..., ge=1, le=15, description="Number of bedrooms", example=4)
    bathrooms: int = Field(..., ge=1, le=10, description="Number of bathrooms", example=2)
    stories: int = Field(..., ge=1, le=10, description="Number of stories/floors", example=3)
    parking: int = Field(..., ge=0, le=10, description="Number of parking spaces", example=2)
    mainroad: Literal["yes", "no"] = Field(..., description="Located on main road ('yes' or 'no')", example="yes")
    guestroom: Literal["yes", "no"] = Field(..., description="Guest room available ('yes' or 'no')", example="no")
    basement: Literal["yes", "no"] = Field(..., description="Basement available ('yes' or 'no')", example="no")
    hotwaterheating: Literal["yes", "no"] = Field(..., description="Hot water heating available ('yes' or 'no')", example="no")
    airconditioning: Literal["yes", "no"] = Field(..., description="Air conditioning available ('yes' or 'no')", example="yes")
    prefarea: Literal["yes", "no"] = Field(..., description="Located in preferred area ('yes' or 'no')", example="yes")
    furnishingstatus: Literal["furnished", "semi-furnished", "unfurnished"] = Field(
        ..., description="Furnishing status of the house", example="furnished"
    )

    @field_validator("mainroad", "guestroom", "basement", "hotwaterheating", "airconditioning", "prefarea", mode="before")
    @classmethod
    def normalize_binary(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("furnishingstatus", mode="before")
    @classmethod
    def normalize_furnishing(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    prediction_id: int
    predicted_price: float = Field(..., description="Predicted house price in INR", example=10500000.0)
    formatted_price: str = Field(..., description="Formatted price string with currency symbol", example="₹1,05,00,000")
    currency: str = "INR"
    created_at: datetime
    input_features: dict


class PredictionHistoryItem(BaseModel):
    prediction_id: int
    area: float
    bedrooms: int
    bathrooms: int
    stories: int
    parking: int
    mainroad: str
    airconditioning: str
    prefarea: str
    furnishingstatus: str
    predicted_price: float
    formatted_price: str
    created_at: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_type: str
    model_algorithm: str
    version: str = "1.0.0"
