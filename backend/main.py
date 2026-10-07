"""
FastAPI Backend Application for House Price Prediction System.
Provides RESTful endpoints for model inference, health checking,
history querying, and serves the web frontend.
"""

import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import engine, get_db, DB_TYPE, Base
from backend.models import PredictionRecord
from backend.schemas import (
    HouseFeaturesInput,
    PredictionResponse,
    HealthResponse,
    PredictionHistoryItem
)
from src.predict import predict_price, format_inr, load_model

# Create DB tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI App
app = FastAPI(
    title="House Price Prediction API",
    description="End-to-End House Price Prediction REST API using Tuned XGBoost Regressor and PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load ML model during startup
try:
    load_model()
    MODEL_LOADED = True
except Exception as e:
    print(f"[Warning] ML Model could not be loaded at startup: {e}")
    MODEL_LOADED = False


# Mount frontend static directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", summary="Root Endpoint")
def read_root():
    """
    Returns API overview and documentation links.
    """
    return {
        "project": "House Price Prediction System",
        "semester": "7th Semester Capstone Project",
        "status": "Operational",
        "primary_model": "Tuned XGBoost Regressor",
        "database": DB_TYPE,
        "endpoints": {
            "web_ui": "/app",
            "swagger_docs": "/docs",
            "health_check": "/health",
            "prediction": "POST /predict",
            "history": "GET /predictions",
            "model_metrics": "GET /model-metrics"
        }
    }


@app.get("/app", summary="Web Frontend Application")
@app.get("/app/", include_in_schema=False)
def serve_frontend():
    """
    Serves the web frontend user interface.
    """
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend interface file not found.")


@app.get("/style.css", include_in_schema=False)
def serve_style():
    """Serves the CSS stylesheet directly at root path."""
    css_file = os.path.join(frontend_dir, "style.css")
    if os.path.exists(css_file):
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="Stylesheet not found.")


@app.get("/script.js", include_in_schema=False)
def serve_script():
    """Serves the JavaScript file directly at root path."""
    js_file = os.path.join(frontend_dir, "script.js")
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Script not found.")


@app.get("/health", response_model=HealthResponse, summary="Health Check")
def health_check():
    """
    Validates the operational state of the API, Model, and Database.
    """
    return HealthResponse(
        status="healthy" if MODEL_LOADED else "degraded",
        model_loaded=MODEL_LOADED,
        database_type=DB_TYPE,
        model_algorithm="XGBoost Regressor (Hyperparameter Tuned)",
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED, summary="Predict House Price")
def predict_house_price(input_data: HouseFeaturesInput, db: Session = Depends(get_db)):
    """
    Predicts the house price given property features and stores the record into the database.
    """
    features_dict = input_data.model_dump()

    try:
        results = predict_price(features_dict)
        pred_item = results[0]
        predicted_val = pred_item["predicted_price"]
        formatted_val = pred_item["formatted_price"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing model prediction: {str(e)}"
        )

    # Save to PostgreSQL/Database
    record = PredictionRecord(
        area=input_data.area,
        bedrooms=input_data.bedrooms,
        bathrooms=input_data.bathrooms,
        stories=input_data.stories,
        parking=input_data.parking,
        mainroad=input_data.mainroad,
        guestroom=input_data.guestroom,
        basement=input_data.basement,
        hotwaterheating=input_data.hotwaterheating,
        airconditioning=input_data.airconditioning,
        prefarea=input_data.prefarea,
        furnishingstatus=input_data.furnishingstatus,
        input_features=json.dumps(features_dict),
        predicted_price=predicted_val,
        created_at=datetime.utcnow()
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        print(f"[Warning] Failed to log prediction to database: {e}")

    return PredictionResponse(
        prediction_id=record.prediction_id or 1,
        predicted_price=predicted_val,
        formatted_price=formatted_val,
        currency="INR",
        created_at=record.created_at or datetime.utcnow(),
        input_features=features_dict
    )


@app.get("/predictions", summary="Get Prediction History")
def get_prediction_history(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Retrieves the most recent prediction records stored in the database.
    """
    records = db.query(PredictionRecord).order_by(PredictionRecord.prediction_id.desc()).limit(limit).all()
    history = []
    for r in records:
        history.append({
            "prediction_id": r.prediction_id,
            "area": r.area,
            "bedrooms": r.bedrooms,
            "bathrooms": r.bathrooms,
            "stories": r.stories,
            "parking": r.parking,
            "mainroad": r.mainroad,
            "airconditioning": r.airconditioning,
            "prefarea": r.prefarea,
            "furnishingstatus": r.furnishingstatus,
            "predicted_price": r.predicted_price,
            "formatted_price": format_inr(r.predicted_price),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        })
    return {"total": len(history), "records": history}


@app.get("/model-metrics", summary="Model Performance Summary")
def get_model_metrics():
    """
    Returns comparative evaluation metrics (MAE, RMSE, R2) and tuning parameters.
    """
    metrics_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "model_metrics.json"))
    if os.path.exists(metrics_file):
        with open(metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Metrics not found. Run src/train.py first."}
