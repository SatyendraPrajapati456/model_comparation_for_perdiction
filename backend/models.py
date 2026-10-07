"""
SQLAlchemy ORM Models for House Price Prediction System.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from backend.database import Base


class PredictionRecord(Base):
    """
    Table storing every prediction request and result for audit and analytics.
    """
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    area = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    stories = Column(Integer, nullable=False)
    parking = Column(Integer, nullable=False)
    mainroad = Column(String(10), nullable=False)
    guestroom = Column(String(10), nullable=False)
    basement = Column(String(10), nullable=False)
    hotwaterheating = Column(String(10), nullable=False)
    airconditioning = Column(String(10), nullable=False)
    prefarea = Column(String(10), nullable=False)
    furnishingstatus = Column(String(30), nullable=False)
    
    # Serialized JSON of all features
    input_features = Column(Text, nullable=False)
    predicted_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "prediction_id": self.prediction_id,
            "area": self.area,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "stories": self.stories,
            "parking": self.parking,
            "mainroad": self.mainroad,
            "guestroom": self.guestroom,
            "basement": self.basement,
            "hotwaterheating": self.hotwaterheating,
            "airconditioning": self.airconditioning,
            "prefarea": self.prefarea,
            "furnishingstatus": self.furnishingstatus,
            "input_features": self.input_features,
            "predicted_price": self.predicted_price,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
