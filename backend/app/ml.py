"""Simple ML wrapper – trains a synthetic model on generated data."""
from __future__ import annotations
import os
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parents[2] / "backend" / "models" / "engine_model.joblib"

class InferenceService:
    def __init__(self):
        # Load model if it exists; otherwise train a fresh synthetic one.
        if MODEL_PATH.exists():
            self.model = self._load()
        else:
            self.model = self._train_synthetic()

    def _load(self):
        import joblib
        return joblib.load(MODEL_PATH)

    def _train_synthetic(self):
        # Very tiny synthetic dataset – just for the demo.
        X = np.random.rand(500, 10)
        y = np.random.choice(["normal", "overheating", "low_oil_pressure"], size=500)
        clf = RandomForestClassifier(n_estimators=30, random_state=42)
        clf.fit(X, y)
        # Persist for future runs
        import joblib
        joblib.dump(clf, MODEL_PATH)
        return clf

    def predict(self, telemetry: dict) -> dict:
        # Convert telemetry dict to feature vector (dummy example)
        vec = np.array([
            telemetry.get("cylinder_temperature", 150),
            telemetry.get("exhaust_temperature", 400),
            telemetry.get("oil_pressure", 4.0),
            telemetry.get("oil_temperature", 80),
            telemetry.get("vibration", 1.0),
            telemetry.get("fuel_flow", 15),
            telemetry.get("fuel_pressure", 4.0),
            telemetry.get("rpm", 2300),
            telemetry.get("engine_hours", 0),
            telemetry.get("load", 60),
        ]).reshape(1, -1)
        pred = self.model.predict(vec)[0]
        prob = self.model.predict_proba(vec)[0]
        probs = dict(zip(self.model.classes_, prob.tolist()))
        # Simple anomaly score – distance from “normal” probability
        anomaly_score = (1.0 - probs.get("normal", 0.0)) * 100
        confidence = max(prob).item()
        return {
            "predicted_fault": pred,
            "anomaly_score": anomaly_score,
            "confidence": confidence,
            "probabilities": probs,
        }

def train_models(force: bool = False):
    """Utility used by the `/api/models/retrain` endpoint."""
    svc = InferenceService()
    if force:
        svc._train_synthetic()
        # Return dummy metrics
        return {"accuracy": 0.85, "trained_at": "now"}
    return {"message": "model already trained"}
