"""Runtime registry for per‑UAV digital‑twin instances.

Each UAV gets its own Runtime which holds a DigitalTwin
(and therefore its own simulator state, history, alerts, etc.).
The registry lazily creates a runtime on first access.
"""

from __future__ import annotations

from typing import Dict

from .digital_twin import DigitalTwin
from .database import Database
from .ml import InferenceService


class Runtime:
    """Container for a single UAV's twin state."""

    def __init__(self, uav_id: str, db: Database, inference: InferenceService) -> None:
        self.uav_id = uav_id
        # The DigitalTwin uses the same DB (tables are keyed by engine_id)
        self.twin = DigitalTwin(db, inference)
        self.running: bool = True

    # Proxy helpers used by API routes
    def snapshot(self):
        return self.twin.snapshot()

    def reset(self):
        return self.twin.reset()

    def set_fault(self, fault: str):
        return self.twin.set_fault(fault)

    def update_settings(self, values: dict):
        return self.twin.update_settings(values)

    @property
    def twin_obj(self) -> DigitalTwin:
        """Expose the underlying DigitalTwin (kept for backward compatibility)."""
        return self.twin


class RuntimeRegistry:
    """Simple in‑process registry of Runtime objects."""

    def __init__(self, db: Database, inference: InferenceService) -> None:
        self._registry: Dict[str, Runtime] = {}
        self._db = db
        self._inference = inference
        # Ensure the original demo runtime exists (id = "default")
        self.get_or_create("default")

    def get_or_create(self, uav_id: str) -> Runtime:
        if uav_id not in self._registry:
            self._registry[uav_id] = Runtime(uav_id, self._db, self._inference)
        return self._registry[uav_id]

    def all_ids(self) -> list[str]:
        return list(self._registry.keys())
