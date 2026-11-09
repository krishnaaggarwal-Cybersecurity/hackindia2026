"""Remote AI inference adapter – uses an external LLM/ML service."""
import os, json, httpx
from .ml import InferenceService  # fallback if env vars not set

class RemoteAdapter:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "").lower()
        self.key = os.getenv("AI_PROVIDER_KEY", "")
        if not (self.provider and self.key):
            raise RuntimeError("Remote AI provider or key not configured")

        self.endpoint = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        }[self.provider]

    async def predict(self, telemetry: dict) -> dict:
        payload = {
            "model": "gpt-4o-mini" if self.provider == "openai" else "gemini-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an engine‑health model. Return JSON with fields: predicted_fault, anomaly_score, confidence, probabilities."
                },
                {"role": "user", "content": json.dumps(telemetry)},
            ],
        }
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.endpoint, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            # OpenAI & Gemini have slightly different response shapes; normalize:
            if self.provider == "openai":
                text = data["choices"][0]["message"]["content"]
            else:  # gemini
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)

# The public InferenceService used by the rest of the app picks the adapter:
class InferenceService:
    def __init__(self):
        try:
            self.adapter = RemoteAdapter()
        except Exception:
            self.adapter = InferenceService()  # fall back to local model (circular import avoided by renaming)
    async def predict(self, telemetry: dict) -> dict:
        return await self.adapter.predict(telemetry)
