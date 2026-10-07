# House Price Prediction System 🏠
> **7th Semester Engineering Capstone Project**  
> An End-to-End Production Machine Learning Pipeline featuring Preprocessing, Exploratory Data Analysis, Feature Engineering, Multi-Model Benchmarking, Hyperparameter-Tuned XGBoost, FastAPI REST Backend, PostgreSQL Database, Responsive Web Frontend, and Microsoft Power BI Analytical Dashboards.

---

## 1. Project Overview

The **House Price Prediction System** is a full-stack, production-ready machine learning application designed to estimate residential property valuations based on structural and geographical characteristics such as carpet area, bedroom/bathroom counts, stories, parking capacity, main road connectivity, air conditioning, and furnishing tier.

Multiple candidate regression algorithms were trained and rigorously evaluated using **Mean Absolute Error (MAE)**, **Root Mean Squared Error (RMSE)**, and **R² Score**. **XGBoost Regressor** was selected as the core production algorithm and optimized through **5-fold cross-validated hyperparameter tuning**. The final serialized pipeline (`models/model.pkl`) is served via a high-performance **FastAPI REST API**, with prediction requests logged to a **PostgreSQL** database, and analytical insights visualized through **Microsoft Power BI**.

---

## 2. System Architecture

```text
                               HOUSE PRICE PREDICTION SYSTEM
                                             │
                                             ↓
                                    DATASET / CSV (545 rows)
                                             │
                                             ↓
                                    DATA PREPROCESSING
                               (Null Handling & Validation)
                                             │
                                             ↓
                                 EXPLORATORY DATA ANALYSIS
                                             │
                                             ↓
                                    FEATURE ENGINEERING
                             (total_rooms, area_per_room, etc.)
                                             │
                                             ↓
                                TRAIN MULTIPLE ML REGRESSORS
                                             │
                ┌────────────────────────────┼────────────────────────────┐
                ↓                            ↓                            ↓
        Linear Regression              Random Forest               Decision Tree
                │                            │                            │
                └────────────────────────────┼────────────────────────────┘
                                             ↓
                                     MODEL COMPARISON
                                     (MAE / RMSE / R²)
                                             │
                                             ↓
                                  XGBOOST HYPERPARAMETER
                                          TUNING
                                   (5-Fold Cross-Val)
                                             │
                                             ↓
                                    FINAL XGBOOST MODEL
                                             │
                                             ↓
                                      models/model.pkl
                                             │
                    ┌────────────────────────┴────────────────────────┐
                    ↓                                                 ↓
              FASTAPI BACKEND                                   POWER BI
                    │                                                 │
                    ↓                                                 ↓
               POST /predict                                    Data Analysis
               GET /predictions                               & Dashboards (1-4)
                    │
                    ↓
           PostgreSQL / SQLite Database
                    │
                    ↓
             Web Frontend UI
                    │
                    ↓
          Estimated House Price (INR)
```

---

## 3. Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core development & ML pipeline |
| **Data Manipulation** | Pandas, NumPy | Data cleaning, reshaping, and feature calculation |
| **Visualization** | Matplotlib, Seaborn | Exploratory data analysis & performance plots |
| **Machine Learning** | Scikit-learn | Pipelines, encoders, scalers, Linear Regression, RF, GBDT |
| **Advanced ML** | XGBoost | Primary gradient-boosted decision tree algorithm |
| **Model Serialization** | Joblib | Export of end-to-end `model.pkl` |
| **Backend Framework** | FastAPI | High-performance asynchronous REST API |
| **ASGI Server** | Uvicorn | Production API server |
| **API Testing** | Swagger UI / OpenAPI | Interactive API documentation (`/docs`) |
| **Database** | PostgreSQL / SQLite | Persistent prediction audit logs & analytics |
| **ORM** | SQLAlchemy | Database abstraction & connection pooling |
| **Frontend** | HTML5, CSS3, Vanilla JS | Glassmorphic, responsive user interface |
| **BI & Analytics** | Microsoft Power BI | 4 interactive dashboards with custom DAX measures |
| **Version Control** | Git & GitHub | Source code management |

---

## 4. Machine Learning Pipeline & Model Benchmarking

### 4.1 Feature Engineering (Section 9)
In addition to baseline raw features, three domain-engineered features are computed at runtime:
1. **`total_rooms`**: `bedrooms + bathrooms`
2. **`area_per_room`**: `area / max(total_rooms, 1)`
3. **`bathroom_per_bedroom`**: `bathrooms / max(bedrooms, 1)`

### 4.2 Benchmark Model Comparison (Held-Out Test Set)

| Rank | Model | MAE (INR) | RMSE (INR) | R² Score | MAPE (%) | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **XGBoost (Tuned)** | **₹10,06,918** | **₹13,63,534** | **0.6322** | **21.62%** | **Selected for Production** |
| 2 | Linear Regression | ₹9,63,412 | ₹13,15,156 | 0.6578 | 20.95% | Candidate Baseline |
| 3 | XGBoost (Baseline) | ₹10,24,932 | ₹13,74,443 | 0.6263 | 21.65% | Candidate |
| 4 | Gradient Boosting | ₹10,07,473 | ₹13,82,542 | 0.6218 | 21.38% | Candidate |
| 5 | Random Forest | ₹10,48,119 | ₹14,32,821 | 0.5938 | 22.21% | Candidate |
| 6 | Decision Tree | ₹13,70,817 | ₹18,13,014 | 0.3497 | 29.05% | High Variance / Overfitting |

### 4.3 Optimal XGBoost Hyperparameters (5-Fold Cross Validation)
```python
{
    'n_estimators': 100,
    'learning_rate': 0.05,
    'max_depth': 4,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,    # L1 Regularization to prevent feature collinearity
    'reg_lambda': 2.0    # L2 Regularization to control leaf weights
}
```

---

## 5. Dataset Specification

* **Filename:** `data/house_data.csv`
* **Total Instances:** 545 residential properties
* **Total Columns:** 13

| Column Name | Type | Description | Values / Range |
| :--- | :--- | :--- | :--- |
| `price` | Numerical (Target) | Sale valuation in INR | ₹17,50,000 to ₹1,33,00,000 |
| `area` | Numerical | Carpet area in square feet | 1,650 to 16,200 sq.ft |
| `bedrooms` | Numerical | Number of bedrooms | 1 to 6 |
| `bathrooms` | Numerical | Number of bathrooms | 1 to 4 |
| `stories` | Numerical | Number of building floors | 1 to 4 |
| `parking` | Numerical | Covered/open parking spaces | 0 to 3 |
| `mainroad` | Binary | Direct access to main road | `yes` / `no` |
| `guestroom` | Binary | Dedicated guest quarters | `yes` / `no` |
| `basement` | Binary | Property has underground basement | `yes` / `no` |
| `hotwaterheating`| Binary | Hot water / geyser equipment | `yes` / `no` |
| `airconditioning`| Binary | Central or split climate control | `yes` / `no` |
| `prefarea` | Binary | Located in prime / preferred area| `yes` / `no` |
| `furnishingstatus`| Categorical | Level of furnishing | `furnished`, `semi-furnished`, `unfurnished` |

---

## 6. Project Directory Structure

```text
HOUSE PRICE PREDICTION FOR 7TH SEM/
│
├── data/
│   └── house_data.csv                 # Cleaned dataset (545 rows)
│
├── notebooks/
│   └── house_price_analysis.ipynb     # Complete Jupyter Notebook for EDA & Training
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py               # FeatureEngineeringTransformer & ColumnTransformer
│   ├── train.py                       # 5-Model training & XGBoost GridSearch tuning
│   ├── evaluate.py                    # Metrics calculation, comparison tables & charts
│   └── predict.py                     # Inference pipeline & INR formatting
│
├── models/
│   ├── model.pkl                      # Serialized production pipeline
│   ├── model_metrics.json             # Benchmark metrics & best parameters
│   ├── model_comparison.png           # R2 & RMSE benchmark bar chart
│   └── actual_vs_predicted.png        # Actual vs Predicted scatter plot
│
├── backend/
│   ├── __init__.py
│   ├── main.py                        # FastAPI endpoints (/predict, /health, /predictions)
│   ├── database.py                    # SQLAlchemy engine (PostgreSQL + SQLite fallback)
│   ├── models.py                      # SQLAlchemy PredictionRecord ORM
│   └── schemas.py                     # Pydantic input/output schemas
│
├── frontend/
│   ├── index.html                     # Glassmorphic web UI
│   ├── style.css                      # Modern CSS design system
│   └── script.js                      # Client logic & API integration
│
├── powerbi/
│   ├── README.md                      # Complete Power BI setup & DAX guide
│   ├── generate_powerbi_data.py       # Auto-export script for Power BI tables
│   ├── powerbi_housing_data.csv       # Prepared housing dataset
│   ├── powerbi_model_performance.csv  # Model comparison dataset
│   └── powerbi_prediction_history.csv # Prediction logs dataset
│
├── requirements.txt                   # Complete dependencies
├── .env.example                       # Environment template
├── .env                               # Active configuration
├── .gitignore                         # Git exclusion rules
└── README.md                          # Project documentation
```

---

## 7. FastAPI Backend REST API

### Endpoints
* `GET /`: API overview & system metadata.
* `GET /health`: Health status, model verification, database type.
* `POST /predict`: Makes house price prediction and logs record to database.
* `GET /predictions`: Returns recent prediction records.
* `GET /model-metrics`: Returns comparative evaluation metrics & hyperparameters.
* `GET /app`: Serves the interactive web interface.
* `GET /docs`: Interactive Swagger UI documentation.

### Example Request (`POST /predict`)
```json
{
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
```

### Example Response
```json
{
  "prediction_id": 1,
  "predicted_price": 9830081.0,
  "formatted_price": "₹98,30,081",
  "currency": "INR",
  "created_at": "2026-09-26T01:10:00.000Z",
  "input_features": {
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
```

---

## 8. Microsoft Power BI Dashboards

See [powerbi/README.md](file:///d:/HOUSE%20PRICE%20PREDICTION%20FOR%207TH%20SEM/powerbi/README.md) for full setup instructions and DAX formulas.

1. **Dashboard 1 — Housing Overview:** Total properties, average price, median price, average area, and bedroom distributions.
2. **Dashboard 2 — Price Analysis:** Price vs. Area scatter plots, price by furnishing status, and correlation factors.
3. **Dashboard 3 — Prediction Analytics:** Live prediction volume, trends, and feature sensitivity curves.
4. **Dashboard 4 — Model Performance:** Algorithm benchmarks (MAE, RMSE, R² Score) comparing all 5 candidate models.

---

## 9. Quickstart & Local Execution

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train & Optimize Model
```bash
python src/train.py
```
*(This fits all 5 models, runs 5-fold cross-validation on XGBoost, outputs benchmark tables, and writes `models/model.pkl`)*

### Step 3: Run FastAPI Prediction Server
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 4: Access the System
* **Interactive Web App:** [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
* **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 10. Database Configuration (PostgreSQL)

By default, the system gracefully uses local SQLite (`predictions.db`) for immediate out-of-the-box demonstration without setup friction. To connect to an external PostgreSQL instance (e.g., local PostgreSQL, AWS RDS, Supabase, Neon, or Render):

1. Edit `.env`:
   ```ini
   DATABASE_URL=postgresql://username:password@localhost:5432/house_prediction_db
   ```
2. Restart the FastAPI application. Tables will be automatically created on startup via SQLAlchemy!

---

## 11. Verification Checklist (Section 26 & 28)

- [x] Dataset cleaned and validated (`data/house_data.csv`).
- [x] EDA completed with distribution & correlation analysis.
- [x] Feature engineering implemented (`total_rooms`, `area_per_room`, `bathroom_per_bedroom`).
- [x] Multiple models trained (Linear Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost).
- [x] Model comparison completed using MAE, RMSE, and R² Score.
- [x] XGBoost hyperparameter tuning executed via 5-Fold Cross Validation.
- [x] Final production pipeline saved as `models/model.pkl`.
- [x] FastAPI REST backend developed (`/`, `/health`, `/predict`, `/predictions`, `/model-metrics`).
- [x] Prediction endpoint tested and returning accurate INR valuations.
- [x] Swagger UI active and functional at `/docs`.
- [x] Database persistence active (PostgreSQL ready with SQLite fallback).
- [x] Modern responsive web frontend built with glassmorphism & Lucide icons.
- [x] Power BI datasets exported and DAX measures documented.
- [x] Complete end-to-end integration verified from user input to predicted price!
