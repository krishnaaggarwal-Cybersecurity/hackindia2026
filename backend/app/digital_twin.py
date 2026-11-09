"""Continuously evolving virtual representation of the synthetic engine."""
from __future__ import annotations
from collections import deque
from copy import deepcopy
import json
import time
from typing import Any

from .config import ENGINE_ID, MAX_HISTORY
from .database import Database
from .ml import InferenceService
from .simulation import EngineSimulator, FAULT_LABELS

PHASES = [
    ("Takeoff", 84, 8), ("Climb", 78, 12), ("Cruise", 62, 75),
    ("Surveillance", 55, 95), ("Loiter", 48, 55), ("Return", 64, 50), ("Landing", 52, 8),
]

class DigitalTwin:
    def __init__(self, database: Database, inference: InferenceService) -> None:
        self.database = database
        self.inference = inference
        self.simulator = EngineSimulator()
        self.running = True
        self.history: deque[dict[str, Any]] = deque(maxlen=MAX_HISTORY)
        self.alerts: deque[dict[str, Any]] = deque(maxlen=60)
        self.last_alert_at: dict[str, float] = {}
        self.current: dict[str, Any] = {}
        self._last_persist = 0.0
        self._last_prediction_persist = 0.0
        self.step()

    def reset(self) -> None:
        self.simulator.reset()
        self.history.clear()
        self.alerts.clear()
        self.last_alert_at.clear()
        self.current = {}
        self.running = True
        self.step()
        self._alert(
            "INFO",
            "Simulation reset to healthy synthetic baseline.",
            "reset",
            "The generic engine twin is now running in Demo Mode."
        )

    def step(self) -> dict[str, Any]:
        if not self.running and self.current:
            return self.snapshot()
        telemetry = self.simulator.step()
        prediction = self.inference.predict(telemetry)
        components, health = self._calculate_health(telemetry, prediction)
        rul = self._calculate_rul(health, telemetry["engine_hours"])
        mission = self._mission(health, prediction["anomaly_score"])
        maintenance = self._maintenance(prediction, components, health)
        twin = {
            "engine_id": ENGINE_ID,
            "operating_state": "RUNNING" if self.running else "PAUSED",
            "simulated": True,
            "telemetry": telemetry,
            "health": health,
            "component_health": components,
            "prediction": prediction,
            "estimated_rul_hours": rul,
            "mission": mission,
            "maintenance": maintenance,
            "settings": self.settings(),
            "updated_at": telemetry["timestamp"],
        }
        self.history.append(twin)
        self.current = twin
        self._generate_alerts(twin)
        now = time.monotonic()
        if now - self._last_persist > 2:
            self.database.save_telemetry({**telemetry, "health_index": health["overall"], "anomaly_score": prediction["anomaly_score"]})
            self._last_persist = now
        if now - self._last_prediction_persist > 8:
            self.database.event(
                "predictions",
                {
                    "timestamp": telemetry["timestamp"],
                    "engine_id": ENGINE_ID,
                    "predicted_fault": prediction["predicted_fault"],
                    "confidence": prediction["confidence"],
                    "probabilities": json.dumps(prediction["probabilities"]),
                },
            )
            self.database.event(
                "missions",
                {
                    "timestamp": telemetry["timestamp"],
                    "engine_id": ENGINE_ID,
                    "reliability": mission["reliability_score"],
                    "payload": json.dumps(mission),
                },
            )
            self._last_prediction_persist = now
        return self.snapshot()

    # -----------------------------------------------------------------
    # The rest of the class (settings, update_settings, set_fault,
    # snapshot, history_data, _ratio, _calculate_health, _calculate_rul,
    # _mission, _maintenance, etc.) is exactly the same as the original
    # file you already have in the archive. Copy it unchanged.
    # -----------------------------------------------------------------
