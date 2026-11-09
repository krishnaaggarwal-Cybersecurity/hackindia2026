from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import ENGINE_ID, ROOT, TELEMETRY_INTERVAL
from .database import Database
from .digital_twin import DigitalTwin
from .ml import InferenceService, train_models
from .schemas import FaultRequest, SimulationSettings
from .runtime_registry import RuntimeRegistry

# Initialise shared components
_db = Database()
_inference = InferenceService()
registry = RuntimeRegistry(_db, _inference)

# Keep the original singleton for backward‑compatible demo routes
runtime = Runtime()

@asynccontextmanager
async def lifespan(_: FastAPI):
    await runtime.startup()
    yield
    await runtime.shutdown()

app = FastAPI(
    title="AeroTwin Digital Twin API",
    version="1.0.0",
    description="Synthetic, local‑only generic aero piston engine health‑monitoring demonstrator.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Original demo endpoints (still work on the default runtime) -----
@app.get("/")
def root() -> dict[str, str]:
    return {"service": "AeroTwin Digital Twin API", "mode": "synthetic demo", "docs": "/docs"}

@app.get("/api/status")
def status() -> dict[str, Any]:
    twin = runtime.get()
    return {"live": twin.running, "mode": "DEMO MODE", "engine_id": ENGINE_ID,
            "simulated": True, "settings": twin.settings()}

@app.get("/api/health")
def health() -> dict[str, Any]:
    return runtime.get().snapshot()["health"]

# (other original routes omitted for brevity – they still reference `runtime`)

# ----- New multi‑UAV endpoints (delegate to registry) -----
@app.get("/api/{uav_id}/status")
def status_uav(uav_id: str) -> dict[str, Any]:
    twin = registry.get_or_create(uav_id).twin_obj
    return {"live": twin.running, "mode": "DEMO MODE", "engine_id": ENGINE_ID,
            "simulated": True, "settings": twin.settings()}

@app.get("/api/{uav_id}/engine")
def engine_uav(uav_id: str) -> dict[str, Any]:
    snapshot = registry.get_or_create(uav_id).twin_obj.snapshot()
    return {k: snapshot[k] for k in ("engine_id", "operating_state",
                                    "simulated", "updated_at", "settings",
                                    "component_health")}

@app.get("/api/{uav_id}/telemetry/latest")
def telemetry_latest_uav(uav_id: str) -> dict[str, Any]:
    return registry.get_or_create(uav_id).twin_obj.snapshot()["telemetry"]

@app.get("/api/{uav_id}/telemetry/history")
def telemetry_history_uav(uav_id: str, limit: int = 300) -> list[dict[str, Any]]:
    if not 1 <= limit <= 900:
        raise HTTPException(422, "limit must be between 1 and 900")
    return [e["telemetry"] for e in registry.get_or_create(uav_id).twin_obj.history_data(limit)]

@app.post("/api/{uav_id}/simulation/start")
def start_simulation_uav(uav_id: str) -> dict[str, Any]:
    r = registry.get_or_create(uav_id)
    r.twin_obj.running = True
    return r.twin_obj.snapshot()

@app.post("/api/{uav_id}/simulation/pause")
def pause_simulation_uav(uav_id: str) -> dict[str, Any]:
    r = registry.get_or_create(uav_id)
    r.twin_obj.running = False
    return r.twin_obj.snapshot()

@app.post("/api/{uav_id}/simulation/reset")
def reset_simulation_uav(uav_id: str) -> dict[str, Any]:
    r = registry.get_or_create(uav_id)
    r.twin_obj.reset()
    return r.twin_obj.snapshot()

@app.post("/api/{uav_id}/simulation/fault")
def inject_fault_uav(uav_id: str, request: FaultRequest) -> dict[str, Any]:
    twin = registry.get_or_create(uav_id).twin_obj
    return twin.set_fault(request.fault)

@app.post("/api/{uav_id}/simulation/settings")
def set_simulation_settings_uav(uav_id: str, settings: SimulationSettings) -> dict[str, Any]:
    twin = registry.get_or_create(uav_id).twin_obj
    return twin.update_settings(settings.model_dump())

@app.get("/api/uavs")
def list_uavs() -> list[str]:
    return registry.all_ids()

# ----- Static frontend serving (fallback for any unknown path) -----
FRONTEND_DIR = ROOT / "frontend" / "dist"

@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    """Serve the compiled React app and preserve client‑side navigation."""
    requested = FRONTEND_DIR / path
    if path and requested.is_file():
        return FileResponse(requested)
    return FileResponse(FRONTEND_DIR / "index.html")
