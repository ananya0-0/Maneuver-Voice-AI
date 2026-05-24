"""
main.py — Maneuver "Talk to Founder" Voice AI Agent
Written for livekit-agents v1.5.x

Pipeline: Microphone → LiveKit → STT → LLM (with tools) → TTS → LiveKit → Browser

Run with:
    python main.py dev
"""

import asyncio
import json
import logging
import os
import pathlib
from datetime import datetime
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
    RoomInputOptions,
)
from livekit.plugins import deepgram, openai, silero

from tools import build_tools

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent
KB_PATH  = BASE_DIR / "knowledge_base.md"
LEADS_PATH = BASE_DIR / "leads.json"

# ── Load knowledge base once at startup ───────────────────────────────────────
KNOWLEDGE_BASE = KB_PATH.read_text(encoding="utf-8")

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are Husain Topiwala, founder of Maneuver — an AI strategy and implementation firm based in the UAE (maneuver.ae).
You're on a real-time voice call with someone who just landed on the Maneuver website and clicked "Talk to Founder".

Your background (use naturally, don't recite it like a CV):
- Previously at JP Morgan, Vanguard, and Deloitte leading digital transformation
- Founding team at Think41 — built agentic AI systems and multimodal platforms from 0 to 1
- Co-founded SleevesUp's India practice, scaled it from 1 to 35 people
- Started Maneuver because SMB founders kept getting priced out of the same AI thinking that drives Fortune 500 outcomes

Your personality:
- Warm, direct, and confident — someone who's been in enterprise boardrooms and startup trenches
- You ask sharp questions but never sound like you're filling a form
- Genuinely curious about people's operations and where the real bottlenecks are
- You speak conversationally, in short sentences. No lists, no bullet points — you're talking, not writing
- You're honest: if AI isn't the right move for someone yet, you'll say so on the call
- You don't oversell — the firm's reputation is built on telling people the truth

Your two modes:

MODE 1 — DISCOVERY (default when call starts)
Your goal is to naturally uncover:
1. Who they are (name, role)
2. What business or company they run
3. What industry they're in
4. The operational problem or bottleneck they're dealing with
5. Their timeline
6. Their budget (ask naturally: "do you have a rough budget in mind for this?")

Don't fire all these at once. Let it flow like a real conversation.
Start every call with: "Hey, this is Husain — glad you made it. Tell me what's going on in the business."

Call update_lead_field as soon as you learn each piece of information — don't batch them.

MODE 2 — Q&A (when they ask about Maneuver)
If the visitor asks about what Maneuver does, answer from the knowledge base below.
When answering about services, process, case studies, or the team — also call the appropriate
show_*_slide tool so the UI updates visually for them.

After answering, steer back to discovery: "What made you come across us — is there something specific in the business you're trying to fix?"

When discovery feels complete and the call is wrapping up naturally, call finalize_lead with a summary.

---
KNOWLEDGE BASE:
{KNOWLEDGE_BASE}
---

IMPORTANT RULES:
- Keep responses SHORT. 2-4 sentences max per turn. Voice call, not a pitch deck.
- Never say "As an AI" or break character under any circumstances.
- If someone is rude, stay calm and professional but don't be a pushover.
- Never read out lists or bullets — convert everything to natural spoken sentences.
- Maneuver is UAE-based, serves global clients. Reference this context when relevant.
"""


# ── Lead persistence ───────────────────────────────────────────────────────────
def save_lead(lead: dict):
    """Append or update lead in leads.json"""
    leads = []
    if LEADS_PATH.exists():
        try:
            leads = json.loads(LEADS_PATH.read_text())
        except json.JSONDecodeError:
            leads = []
    lead["captured_at"] = datetime.utcnow().isoformat()
    leads.append(lead)
    LEADS_PATH.write_text(json.dumps(leads, indent=2))
    logger.info(f"Lead saved to {LEADS_PATH}")


# ── RPC sender ─────────────────────────────────────────────────────────────────
class RPCSender:
    """Sends data messages to the frontend via LiveKit data channel."""

    def __init__(self, room: rtc.Room):
        self.room = room

    async def send(self, method: str, payload: dict):
        data = json.dumps({"method": method, "payload": payload}).encode("utf-8")
        try:
            await self.room.local_participant.publish_data(
                data,
                reliable=True,
                topic="agent_rpc",
            )
            logger.info(f"RPC sent: {method} → {payload}")
        except Exception as e:
            logger.warning(f"RPC send failed: {e}")


# ── Agent class (v1.x style) ───────────────────────────────────────────────────
class ManeuverFounderAgent(Agent):
    def __init__(self, lead_store: dict, rpc_sender_fn):
        # Build tools bound to this session's lead store and RPC sender
        tools = build_tools(lead_store, rpc_sender_fn)
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=tools,
        )
        self._rpc = rpc_sender_fn

    async def on_enter(self):
        """Called when the agent session starts — greet the user."""
        await asyncio.sleep(1.0)
        await self.session.say(
            "Hey, this is Husain — glad you made it. "
            "Tell me what's going on in the business.",
            allow_interruptions=True,
        )


# ── Entrypoint ─────────────────────────────────────────────────────────────────
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    lead_store: dict = {}
    rpc = RPCSender(ctx.room)

    async def rpc_sender(method: str, payload: dict):
        await rpc.send(method, payload)
        if method in ("update_lead_field", "lead_finalized"):
            save_lead(lead_store)

    # ── STT ────────────────────────────────────────────────────────────────────
    use_whisper = os.getenv("USE_WHISPER", "false").lower() == "true"
    if use_whisper:
        from livekit.plugins.openai import STT as WhisperSTT
        stt = WhisperSTT(model="whisper-1")
    else:
        stt = deepgram.STT(
            api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            model="nova-2",
            language="en-US",
        )

    # ── LLM (Ollama, local) ────────────────────────────────────────────────────
    lm = openai.LLM(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1",
        api_key="ollama",
        max_completion_tokens=120,
        temperature=0.7,
        extra_body={
            "num_ctx": 2048,
            "keep_alive": "5m",
        },
    )

    # ── TTS ────────────────────────────────────────────────────────────────────
    tts_provider = os.getenv("TTS_PROVIDER", "deepgram")
    if tts_provider == "deepgram":
        from livekit.plugins.deepgram import TTS as DeepgramTTS
        tts = DeepgramTTS(
            api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            model="aura-orion-en",  # deep male voice
        )
    else:
        tts = openai.TTS(voice="alloy")

    # ── VAD ────────────────────────────────────────────────────────────────────
    vad = silero.VAD.load()

    # ── Session state → RPC ────────────────────────────────────────────────────
    agent = ManeuverFounderAgent(lead_store, rpc_sender)

    session = AgentSession(
        stt=stt,
        llm=lm,
        tts=tts,
        vad=vad,
        turn_detection=None,  # uses VAD-based turn detection
    )

    # Forward session state to frontend
    @session.on("agent_state_changed")
    def on_state_changed(ev):
        state = str(ev.new_state).lower().replace("agentstate.", "")
        asyncio.ensure_future(rpc.send("agent_state", {"state": state}))

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )

    # Keep alive for the duration of the call
    await asyncio.sleep(3600)


# ── Worker bootstrap ───────────────────────────────────────────────────────────
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )