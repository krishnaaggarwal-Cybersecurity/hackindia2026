from __future__ import annotations
from pydantic import BaseModel, Field

class FaultRequest(BaseModel):
    fault: str = Field(..., description="Name of the fault to inject (e.g. 'overheating')")

class SimulationSettings(BaseModel):
    speed: float | None = None
    throttle: float | None = None
    load: float | None = None
    altitude: float | None = None
    ambient_temperature: float | None = None
    active_fault: str | None = None
