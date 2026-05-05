from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
import uvicorn
from catboost import CatBoostClassifier
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        model = CatBoostClassifier()
        model.load_model("production_churn_model.cbm")
        ml_models["cat_clf"] = model
    except Exception as e:
        raise RuntimeError(f"CRITICAL: failed to load model artifact. {e}")
    yield
    ml_models.clear()


# 1. Initialize the FastAPI Application
app = FastAPI(title="Telecom Churn Inference API", version="1.0", lifespan=lifespan)

# 2. Load the Model into Memory on Startup
# Loading it globally ensures it only loads once, not on every single request.

# The mathematically optimal threshold calculated from the PR-Curve
OPTIMAL_THRESHOLD = 0.64


# 3. Define the Strict Data Contract (Pydantic)
# This mirrors the exact raw columns the model was trained on.
class CustomerPayload(BaseModel):
    customerID: str
    gender: str
    SeniorCitizen: int = Field(ge=0, le=1, description="1 if senior citizen, else 0")
    Partner: str
    Dependents: str
    tenure: int = Field(ge=0, description="Months the customer has stayed")
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: str = Field(
        description="Often comes in as a string with blank spaces"
    )


# 4. The Exact Feature Engineering Function from Training
def engineer_churn_features(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = df.copy()
    df_feat["TotalCharges"] = pd.to_numeric(
        df_feat["TotalCharges"], errors="coerce"
    ).fillna(0.0)
    df_feat["Plan_tier"] = np.where(df_feat["MonthlyCharges"] > 35, "Premium", "Basic")
    df_feat["Discretionary_Spend"] = (df_feat["MonthlyCharges"] - 20.0).clip(lower=0)

    bins = [-1, 6, 60, 200]
    labels = ["Onboarding", "Established", "Veteran"]
    df_feat["Customer_Lifecycle"] = pd.cut(
        df_feat["tenure"], bins=bins, labels=labels
    ).astype(str)

    df_feat["Is_New_Customer"] = (df_feat["tenure"] <= 3).astype(int)
    df_feat["Implied_Total_Diff"] = df_feat["TotalCharges"] - (
        df_feat["MonthlyCharges"] * df_feat["tenure"]
    )

    return df_feat


# 5. The Core Inference Endpoint
@app.post("/predict_churn")
async def predict_churn(customer: CustomerPayload):
    try:
        # Convert the validated JSON payload directly into a Pandas DataFrame
        df_raw = pd.DataFrame([customer.model_dump()])

        # Pass the raw data through the feature engineering pipeline
        df_processed = engineer_churn_features(df_raw)

        # Drop identifiers to match the training shape
        if "customerID" in df_processed.columns:
            df_processed = df_processed.drop(columns=["customerID"])

        # Reorder columns to match model's expected feature order
        expected_features = [
            "gender",
            "SeniorCitizen",
            "Partner",
            "Dependents",
            "tenure",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod",
            "MonthlyCharges",
            "TotalCharges",
            "Plan_tier",
            "Discretionary_Spend",
            "Customer_Lifecycle",
            "Is_New_Customer",
            "Implied_Total_Diff",
        ]
        df_processed = df_processed[expected_features]

        model = ml_models.get("cat_clf")

        if not model:
            raise HTTPException(
                status_code=503, detail="Model is currently unavailable"
            )
        # Execute the prediction to get the raw probability (Index 1 for Churn)
        churn_prob = model.predict_proba(df_processed)[0][1]

        # Apply the business threshold logic
        is_high_risk = bool(churn_prob >= OPTIMAL_THRESHOLD)

        # Return the final actionable response to the frontend/CRM
        return {
            "customer_id": customer.customerID,
            "churn_probability": round(float(churn_prob), 3),
            "risk_assessment": "High Risk - Requires Retention Action"
            if is_high_risk
            else "Low Risk - Safe",
            "threshold_applied": OPTIMAL_THRESHOLD,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# For running locally during testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
