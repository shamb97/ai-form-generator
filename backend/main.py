# --- Load environment first ---
import os, json, re
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)  # 👈 explicitly point to backend/.env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is alive"}

# Allow calls from local dev frontends (Vite/React/Next)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

class EchoIn(BaseModel):
    message: str
    meta: dict | None = None

@app.post("/echo")
def echo(payload: EchoIn):
    return {"you_sent": payload.model_dump()}

# --- Optional: skeleton AI endpoint (no external call yet) ---
class ChatIn(BaseModel):
    prompt: str

@app.post("/ai/draft")
def ai_draft(input: ChatIn):
    # In future: call your chosen model here using env keys
    # For now, just return a stub
    return {
        "model": "placeholder",
        "prompt_received": input.prompt,
        "draft": "This is where your AI-generated text will go."
    }
