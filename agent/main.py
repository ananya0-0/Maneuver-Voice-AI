"""
main.py — Maneuver "Talk to Founder" Voice AI Agent

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
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero

from tools import build_tools

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths 
BASE_DIR = pathlib.Path(__file__).parent
KB_PATH = BASE_DIR / "knowledge_base.md"
LEADS_PATH = BASE_DIR / "leads.json"

# Load knowledge base once at startup 
KNOWLEDGE_BASE = KB_PATH.read_text(encoding="utf-8")

# System prompt 
SYSTEM_PROMPT = f"""You are Husain Topiwala, founder of Maneuver — an AI strategy and implementation firm based in the UAE (maneuver.ae).
You're on a real-time voice call with someone who just landed on the Maneuver website and clicked "Talk to Founder".

Your background (use naturally, don't recite it):
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
2. What business/company they run
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
- If there's silence, after a few seconds say "Still with me?" naturally.
- Never read out lists or bullets — convert everything to natural spoken sentences.
- Maneuver is UAE-based, serves global clients. Reference this context when relevant.
"""


# Lead persistence 
def save_lead(lead: dict):
    """Append lead to leads.json"""
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


# RPC sender helper 
class RPCSender:
    """Sends RPC messages to all participants in the room (i.e., the frontend)."""

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


# Agent entrypoint 
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    lead_store: dict = {}
    rpc = RPCSender(ctx.room)

    async def rpc_sender(method: str, payload: dict):
        await rpc.send(method, payload)
        # Also persist lead updates in real time
        if method in ("update_lead_field", "lead_finalized"):
            save_lead(lead_store)

    # Build tool list
    tools = build_tools(lead_store, rpc_sender)

    # STT setup
    use_whisper = os.getenv("USE_WHISPER", "false").lower() == "true"
    if use_whisper:
        # Whisper runs fully locally — no API key needed
        from livekit.plugins.openai import STT as WhisperSTT
        stt = WhisperSTT.with_groq(model="whisper-large-v3")
    else:
        stt = deepgram.STT(
            api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            model="nova-2",
            language="en-US",
        )

    # LLM setup (Ollama, fully local) 
    livekit_llm = openai.LLM.with_ollama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    # TTS setup 
    tts_provider = os.getenv("TTS_PROVIDER", "kokoro")
    if tts_provider == "kokoro":
        from livekit.plugins import kokoro
        tts = kokoro.TTS(voice="af_heart")
    else:
        # Fallback: OpenAI TTS (requires OPENAI_API_KEY)
        tts = openai.TTS(voice="alloy")

    # VAD (Voice Activity Detection)
    vad = silero.VAD.load()

    # Assemble the pipeline 
    initial_ctx = llm.ChatContext().append(role="system", text=SYSTEM_PROMPT)

    assistant = VoiceAssistant(
        vad=vad,
        stt=stt,
        llm=livekit_llm,
        tts=tts,
        chat_ctx=initial_ctx,
        fnc_ctx=llm.FunctionContext(tools),
        # How long of a silence (seconds) before the agent considers a turn complete
        min_endpointing_delay=0.6,
        # If the user starts speaking while agent is talking, stop and listen
        allow_interruptions=True,
    )

    # Agent state → RPC for UI indicator 
    @assistant.on("agent_started_speaking")
    def on_speaking():
        asyncio.ensure_future(rpc.send("agent_state", {"state": "speaking"}))

    @assistant.on("agent_stopped_speaking")
    def on_stopped():
        asyncio.ensure_future(rpc.send("agent_state", {"state": "listening"}))

    @assistant.on("user_started_speaking")
    def on_user_speaking():
        asyncio.ensure_future(rpc.send("agent_state", {"state": "listening"}))

    @assistant.on("agent_speech_interrupted")
    def on_interrupted():
        asyncio.ensure_future(rpc.send("agent_state", {"state": "listening"}))

    # Start the assistant 
    assistant.start(ctx.room)

    # Greet the user as soon as they connect
    await asyncio.sleep(1.5)
    await assistant.say(
        "Hey, this is Husain — glad you made it. Tell me what's going on in the business.",
        allow_interruptions=True,
    )

    # Keep the agent alive for the duration of the call
    await asyncio.sleep(3600)


# Worker bootstrap 
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
