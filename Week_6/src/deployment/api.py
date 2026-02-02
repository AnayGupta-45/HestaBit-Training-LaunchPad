from fastapi import FastAPI, HTTPException, Request
from pydantic import create_model
import pandas as pd
import joblib
import json
import uuid
from pathlib import Path
from datetime import datetime
from time import time

MODEL_PATH = Path("src/models/best_model.pkl")
FEATURE_PATH = Path("src/features/feature_list.json")
LOG_PATH = Path("src/logs/prediction_logs.csv")

MODEL_VERSION = "logreg_l2_c0.01_v1.0.0"

app = FastAPI(title="Churn Prediction API")

model = joblib.load(MODEL_PATH)

with open(FEATURE_PATH) as f:
    FEATURES = json.load(f)

FeatureSchema = create_model(
    "FeatureSchema",
    **{feature: (float, ...) for feature in FEATURES}
)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.post("/predict")
def predict(request: FeatureSchema, fastapi_request: Request):
    request_id = fastapi_request.state.request_id
    start = time()

    try:
        df = pd.DataFrame([request.dict()])[FEATURES]
        prob = model.predict_proba(df)[0][1]
        prediction = int(prob >= 0.5)
        latency_ms = int((time() - start) * 1000)

        log_row = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "model_version": MODEL_VERSION,
            "prediction": prediction,
            "probability": prob,
            "latency_ms": latency_ms,
            **request.dict()
        }

        pd.DataFrame([log_row]).to_csv(
            LOG_PATH,
            mode="a",
            header=not LOG_PATH.exists(),
            index=False
        )

        return {
            "request_id": request_id,
            "prediction": prediction,
            "churn_probability": round(prob, 4)
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Prediction failed")
