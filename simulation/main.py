import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.app.simulation import EngineSimulator, FAULT_LABELS

app = FastAPI()

_sim = EngineSimulator()

@app.post("/start")
def start():
    _sim.running = True
    return {"status": "started"}

@app.post("/pause")
def pause():
    _sim.running = False
    return {"status": "paused"}

@app.post("/reset")
def reset():
    _sim.reset()
    return {"status": "reset"}

@app.post("/fault")
def fault(fault: str):
    _sim.set_fault(fault)
    return {"status": f"fault {fault} injected"}

@app.get("/snapshot")
def snapshot():
    return _sim.step()

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json(_sim.step())
            await asyncio.sleep(0.25)
    except WebSocketDisconnect:
        pass
