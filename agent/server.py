"""
server.py — FastAPI server exposing the /leads endpoint and LiveKit token generation.

Run alongside main.py:
    uvicorn server:app --port 8000 --reload
"""

import json
import os
import pathlib
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from livekit import api

load_dotenv()

app = FastAPI(title="Maneuver Agent Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = pathlib.Path(__file__).parent
LEADS_PATH = BASE_DIR / "leads.json"


@app.get("/token")
async def get_token(room: str = "maneuver-room", participant: str = "visitor"):
    """
    Generate a LiveKit access token for the frontend to join a room.
    The React app calls this endpoint on page load.
    """
    lk_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    lk_api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")

    token = (
        api.AccessToken(lk_api_key, lk_api_secret)
        .with_identity(participant)
        .with_name(participant)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    return {
        "token": token,
        "url": os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        "room": room,
    }


@app.get("/leads")
async def get_leads():
    """Return all captured lead records."""
    if not LEADS_PATH.exists():
        return []
    try:
        return json.loads(LEADS_PATH.read_text())
    except json.JSONDecodeError:
        return []


@app.delete("/leads")
async def clear_leads():
    """Clear all leads (dev utility)."""
    if LEADS_PATH.exists():
        LEADS_PATH.write_text("[]")
    return {"message": "Leads cleared"}


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
