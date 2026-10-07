# Microsoft Power BI Dashboards — House Price Prediction System

This directory contains the ready-to-use data exports and comprehensive blueprint for the **Microsoft Power BI** analytical reports for the 7th Semester House Price Prediction System.

---

## 📊 Overview of 4 Power BI Dashboards

### 🏠 Dashboard 1: Housing Overview
**Purpose:** Provide top-level executive KPIs on the residential real estate market.
* **Cards / KPIs:**
  - `Total Properties`: Count of properties listed
  - `Average Price`: Mean listing valuation
  - `Median Price`: Robust central tendency
  - `Average Area`: Average square footage
  - `Average Bedrooms`: Average bedroom count
* **Key Visuals:**
  - Donut chart: Property distribution by Furnishing Status (`Furnished`, `Semi-Furnished`, `Unfurnished`)
  - Slicers: Filter by `Main Road Access`, `Air Conditioning`, `Preferred Area`

### 💰 Dashboard 2: Price Analysis
**Purpose:** Deep dive into how structural characteristics impact property valuation.
* **Visuals:**
  - **Scatter Plot (Price vs Area):** Scatter plot with trend line showing positive elasticity of price with area
  - **Clustered Column Chart (Price vs Bedrooms):** Comparison of average price across 1 to 6 bedrooms
  - **Bar Chart (Price vs Bathrooms):** Shows premium commanded by properties with multiple bathrooms
  - **Histogram / Area Chart (Price Distribution):** Visualizes property valuation distribution curves
  - **Box & Whisker / Matrix (Price by Furnishing Status):** Median price, IQR, and variance per furnishing tier

### 🔮 Dashboard 3: Prediction Analytics
**Purpose:** Monitor real-time inference activity logged by the FastAPI backend into PostgreSQL.
* **Visuals:**
  - **Card:** Total Predictions Logged
  - **Card:** Average Predicted Price
  - **Line Chart (Prediction Trends):** Time-series graph of predictions made per hour/day
  - **Feature Sensitivity Breakdown:** Average predicted price grouped by stories, AC, and preferred area

### 🏆 Dashboard 4: Model Performance
**Purpose:** Machine Learning benchmarking report comparing candidate algorithms evaluated on held-out test data.
* **Visuals:**
  - **Horizontal Bar Chart (R² Score):** Tuned XGBoost vs Linear Regression vs Random Forest vs Gradient Boosting vs Decision Tree
  - **Clustered Bar Chart (RMSE & MAE):** Error comparison (lower is better)
  - **Table Matrix:** Exact metrics (`MAE`, `RMSE`, `R2 Score`, `MAPE (%)`, `Status`)

---

## 📐 Data Model & Relationships

```
+--------------------------------+           +---------------------------------+
|     powerbi_housing_data       |           |   powerbi_prediction_history    |
+--------------------------------+           +---------------------------------+
| price (Target)                 |           | prediction_id (PK)              |
| area                           |           | area                            |
| bedrooms                       |           | bedrooms                        |
| bathrooms                      |           | bathrooms                       |
| stories                        |           | stories                         |
| parking                        |           | parking                         |
| mainroad                       |           | mainroad                        |
| airconditioning                |           | airconditioning                 |
| prefarea                       |           | prefarea                        |
| furnishingstatus               |           | furnishingstatus                |
| total_rooms                    |           | predicted_price                 |
| area_per_room                  |           | timestamp                       |
| price_per_sqft                 |           +---------------------------------+
| price_bracket                  |
+--------------------------------+
                                             +---------------------------------+
                                             |   powerbi_model_performance    |
                                             +---------------------------------+
                                             | Model                           |
                                             | MAE                             |
                                             | RMSE                            |
                                             | R2 Score                        |
                                             | MAPE (%)                        |
                                             +---------------------------------+
```

---

## 🔢 DAX (Data Analysis Expressions) Formulas

Copy and paste these measures directly into Power BI Desktop:

```dax
// 1. Total Listed Properties
Total Properties = COUNTROWS('powerbi_housing_data')

// 2. Average Listing Price
Average Price = AVERAGE('powerbi_housing_data'[price])

// 3. Median Listing Price
Median Price = MEDIAN('powerbi_housing_data'[price])

// 4. Average Carpet Area
Average Area = AVERAGE('powerbi_housing_data'[area])

// 5. Average Bedrooms
Average Bedrooms = AVERAGE('powerbi_housing_data'[bedrooms])

// 6. Average Price per Sq. Ft.
Avg Price Per SqFt = DIVIDE([Average Price], [Average Area], 0)

// 7. Total Model Inferences Logged
Total Predictions = COUNTROWS('powerbi_prediction_history')

// 8. Average Predicted Valuation
Avg Predicted Price = AVERAGE('powerbi_prediction_history'[predicted_price])

// 9. Best Model R2 Score
Max R2 Score = MAX('powerbi_model_performance'[R2 Score])
```

---

## 🚀 How to Load and Build in Microsoft Power BI Desktop

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** &rarr; Select **Text/CSV**.
3. Import the 3 CSV files from this folder:
   - `powerbi/powerbi_housing_data.csv`
   - `powerbi/powerbi_model_performance.csv`
   - `powerbi/powerbi_prediction_history.csv`
4. In the **Modeling** tab, click **New Measure** and add the DAX formulas provided above.
5. Create pages corresponding to:
   - Page 1: `Housing Overview`
   - Page 2: `Price Analysis`
   - Page 3: `Prediction Analytics`
   - Page 4: `Model Performance`
6. Save the project file as `powerbi/house_price_dashboard.pbix`.
