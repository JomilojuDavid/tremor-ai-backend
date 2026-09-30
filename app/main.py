import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.schemas import SensorData
from app.predictor import predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tremor AI Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cautious-acorn-x9rjrgpxj7xcj97-5173.app.github.dev",
        "https://tremor-glove-dashboard.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_prediction = {}


@app.get("/")
def home():
    return {
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "Random Forest",
        "sensor": "MPU6050",
        "api": "online"
    }


@app.post("/predict")
def classify(data: SensorData):

    global latest_prediction

    prediction, confidence = predict(data)

    labels = {
        0: "No Tremor",
        1: "Mild Tremor",
        2: "Severe Tremor"
    }

    recommendations = {
        0: "No abnormal tremor detected.",
        1: "Continue monitoring.",
        2: "Medical evaluation is recommended."
    }

    latest_prediction = {
        "sensor": {
            "aX": data.aX,
            "aY": data.aY,
            "aZ": data.aZ,
            "gX": data.gX,
            "gY": data.gY,
            "gZ": data.gZ
        },
        "prediction": {
            "severity": int(prediction),
            "label": labels[int(prediction)],
            "confidence": round(confidence * 100, 2),
            "recommendation": recommendations[int(prediction)],
            "timestamp": datetime.now().isoformat()
        }
    }

    stored_prediction = latest_prediction["prediction"]
    logger.info(
        "current_timestamp=%s pid=%s PREDICT RECEIVED sensor=%s "
        "prediction_label=%s prediction_confidence=%s "
        "stored_prediction_timestamp=%s",
        datetime.now().isoformat(),
        os.getpid(),
        latest_prediction["sensor"],
        stored_prediction["label"],
        stored_prediction["confidence"],
        stored_prediction["timestamp"],
    )

    return latest_prediction


@app.get("/latest")
def latest():
    latest_prediction_empty = not latest_prediction
    timestamp = None
    elapsed = None
    returning_prediction = False

    try:
        if not latest_prediction_empty:
            timestamp = latest_prediction.get("prediction", {}).get("timestamp")

            if timestamp:
                try:
                    last_update = datetime.fromisoformat(timestamp)
                    elapsed = (datetime.now() - last_update).total_seconds()

                    # If no new sensor data has arrived for 5 seconds,
                    # consider the device offline / waiting for data.
                    returning_prediction = elapsed <= 5

                except Exception:
                    pass
    finally:
        logger.info(
            "current_timestamp=%s pid=%s latest_prediction_empty=%s "
            "stored_prediction_timestamp=%s elapsed_seconds=%s "
            "returning=%s",
            datetime.now().isoformat(),
            os.getpid(),
            latest_prediction_empty,
            timestamp,
            round(elapsed, 3) if elapsed is not None else None,
            "latest_prediction" if returning_prediction else "{}",
        )

    return latest_prediction if returning_prediction else {}
