from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.schemas import SensorData
from app.predictor import predict

app = FastAPI(
    title="Tremor AI Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cautious-acorn-x9rjrgpxj7xcj97-5173.app.github.dev"
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

    return latest_prediction

@app.get("/latest")
def latest():
    return latest_prediction