# 🗣️ Maneuver — Talk to Founder

A real-time **Voice AI** web app where visitors talk directly to **Husain Topiwala**, founder of [Maneuver](https://maneuver.ae) — an AI strategy and implementation firm based in the UAE.

> Skip the contact form. Have an actual conversation.

---

## ✨ Features

- 🎙️ **Real-time voice** — Speak naturally, the AI responds conversationally
- 🤖 **Local LLM** — Powered by Ollama (Llama/TinyLlama), zero API costs
- 🧠 **Context-aware** — Knows the founder's background, case studies, and services
- 🖼️ **Visual slides** — Ask about services, pricing, or process → see it on screen
- 📋 **Smart lead capture** — Automatically extracts name, company, problem, budget, etc.
- 🌐 **Works in browser** — No app install, just open the link

---

## 🏗️ Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Browser    │◄────►│   LiveKit    │◄────►│   Agent      │
│  (React +    │      │  (WebRTC)    │      │  (Python)    │
│   Vite)      │      │  :7880       │      │               │
└──────────────┘      └──────────────┘      │  ┌─────────┐  │
       ▲                                     │  │Deepgram │  │
       │   /token                            │  │  STT    │  │
       ▼                                     │  └─────────┘  │
┌──────────────┐                             │  ┌─────────┐  │
│   FastAPI    │                             │  │ Ollama  │  │
│  (Token +    │                             │  │  LLM    │  │
│   Leads API) │                             │  └─────────┘  │
│  :8000       │                             │  ┌─────────┐  │
└──────────────┘                             │  │Deepgram │  │
                                             │  │  TTS    │  │
                                             │  └─────────┘  │
                                             │  ┌─────────┐  │
                                             │  │ Silero  │  │
                                             │  │  VAD    │  │
                                             │  └─────────┘  │
                                             └──────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| 🎧 **Voice Pipeline** | [LiveKit Agents](https://github.com/livekit/agents) v1.5 |
| 🗣️ **Speech-to-Text** | Deepgram Nova-2 |
| 🧠 **Language Model** | Ollama + TinyLlama (local, no API key) |
| 🔊 **Text-to-Speech** | Deepgram Aura-Orion (male voice) |
| 🛑 **Voice Activity** | Silero VAD |
| 🌐 **Frontend** | React 18 + Vite |
| 🎨 **UI Components** | [LiveKit Components](https://github.com/livekit/components-js) |
| ⚡ **Token Server** | FastAPI + Uvicorn |
| 🐳 **Infrastructure** | Docker (LiveKit server) |

---

## 📁 Project Structure

```
maneuver-voice-assistant/
├── agent/                          # Python voice agent
│   ├── main.py                     # Agent entrypoint (STT → LLM → TTS)
│   ├── tools.py                    # Tool definitions (lead capture, slides)
│   ├── server.py                   # FastAPI token + leads server
│   ├── knowledge_base.md           # Company info the AI references
│   ├── requirements.txt            # Python dependencies
│   └── venv/                       # Virtual environment
├── frontend/                       # React app
│   ├── src/
│   │   ├── App.jsx                 # Root — room connection
│   │   ├── VoiceInterface.jsx      # Main UI — orb, transcript, controls
│   │   ├── TranscriptPanel.jsx     # Live conversation transcript
│   │   ├── LeadPanel.jsx           # Discovery tracker
│   │   ├── VisualPanel.jsx         # Services/pricing/case studies slides
│   │   └── AgentOrb.jsx            # Animated listening/speaking indicator
│   └── package.json
├── docker-compose.yml              # LiveKit server
└── .env                            # API keys & config
```

---

## 🚀 Quick Start

### 1. Prerequisites

| Tool | Why |
|------|-----|
| [Docker Desktop](https://docker.com) | Runs LiveKit server |
| [Python 3.11+](https://python.org) | Runs the agent |
| [Node.js 18+](https://nodejs.org) | Runs the frontend |
| [Ollama](https://ollama.com) | Runs the LLM locally |

### 2. Start LiveKit

```bash
docker-compose up -d
```

### 3. Install agent dependencies

```bash
cd agent
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Pull the LLM

```bash
ollama pull tinyllama
```

### 5. Configure `.env`

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
DEEPGRAM_API_KEY=your_key_here    # Get one at deepgram.com (free tier works)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
TTS_PROVIDER=deepgram
```

### 6. Launch everything

Open **four terminals**:

| # | Command | Runs |
|---|---------|------|
| 1 | `cd agent && uvicorn server:app --port 8000 --reload` | Token server |
| 2 | `cd agent && python main.py dev` | Voice agent |
| 3 | `cd frontend && npm install && npm run dev` | Web UI |
| 4 | Open **http://localhost:3000** | Click "Start talking" 🎙️ |

---

## 🎯 How It Works

1. **Visitor clicks** "Talk to Founder" → browser requests mic access
2. **Frontend gets a token** from FastAPI → joins a LiveKit room
3. **LiveKit dispatches** the job to the Python agent
4. **Agent greets** the visitor as Husain using Deepgram TTS (male voice)
5. **Conversation flows**:
   - 🎤 Your mic → Deepgram STT → Ollama LLM → Deepgram TTS → 🔈 You hear Husain
   - 🖼️ Ask about services → slide appears on screen
   - 📝 Agent captures name, company, problem, budget automatically
6. **Call ends** → lead summary saved to `agent/leads.json`

---

## 🛠️ Tools the AI Uses

The agent has access to these tools during the call:

| Tool | Trigger | Effect |
|------|---------|--------|
| `update_lead_field` | Learns name, company, role, problem, timeline, budget | Updates on-screen tracker |
| `show_services_slide` | "What do you do?" | Shows services card |
| `show_pricing_slide` | "How much does it cost?" | Shows pricing card |
| `show_process_slide` | "How does it work?" | Shows process steps |
| `show_case_studies_slide` | "Past work?" | Shows case studies |
| `show_team_slide` | "Who's the team?" | Shows team card |
| `finalize_lead` | Call wraps up | Saves lead record |

---

## ⚙️ Configuration

### LLM Models (Ollama)

Edit `.env` to switch models:

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `tinyllama` | 637 MB | ⚡ Fast | Good for conversations |
| `llama3.2:1b` | 1.3 GB | 🏃 Medium | Better quality |
| `llama3` | 4.7 GB | 🐢 Slow | Best quality (needs 16GB+ RAM) |

### Voice Options

| TTS Provider | Voice | Key Required |
|-------------|-------|-------------|
| Deepgram (`deepgram`) | `aura-orion-en` (male) | ✅ Deepgram API key |
| OpenAI (`openai`) | `alloy`, `echo`, `onyx` | ✅ OpenAI API key |

---

## 🐛 Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| ❌ LiveKit container exits | Wrong key format | Use `devkey: secret` (with space) |
| ❌ "Kokoro TTS not available" | Plugin not found | Set `TTS_PROVIDER=deepgram` in `.env` |
| ❌ "Cannot connect to LiveKit" | Docker not running | Run `docker-compose up -d` |
| ❌ Mic not working | Browser permission | Click 🔒 in URL bar → Allow mic |
| ❌ Agent is lagging | LLM too slow | Use `tinyllama` or close other apps |
| ❌ Agent not responding after a few exchanges | Context too large | Already limited to `num_ctx: 2048` |

---

## 📄 API Endpoints (Token Server)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token?room=...&participant=...` | GET | Generate LiveKit join token |
| `/leads` | GET | View captured leads |
| `/leads` | DELETE | Clear all leads |
| `/health` | GET | Health check |

---

## 📸 Preview

```
┌──────────────────────────────────────────────────┐
│  [Maneuver]    ● Listening    2:34    [End call] │
├────────┬─────────────────────────┬───────────────┤
│        │                         │               │
│ 👤 Name│      ╭──────╮          │  ✦ Ask about  │
│ 🏢 Co. │      │  ◉   │          │  services,    │
│ 💼 Role│      │ ████ │          │  pricing, or  │
│ 🔍 Prob│      │ ████ │          │  process...   │
│ 💰 Budg.│      ╰──────╯          │               │
│        │   Husain Topiwala      │               │
│  3/7   │   Founder, Maneuver    │               │
│        │                         │               │
│        │ ┌───────────────────┐  │               │
│        │ │ You: Hey, I run  │  │               │
│        │ │ a logistics...   │  │               │
│        │ │                   │  │               │
│        │ │ Husain: Tell me  │  │               │
│        │ │ more about that. │  │               │
│        │ └───────────────────┘  │               │
└────────┴─────────────────────────┴───────────────┘
```

---

## 🤝 Contributing

This is a project by [Maneuver](https://maneuver.ae). Feel free to fork, open issues, or submit PRs.

---

## 📬 Contact

- **Website:** [maneuver.ae](https://maneuver.ae)
- **Email:** husain@maneuver.ae
- **LinkedIn:** [linkedin.com/company/maneuver-hq](https://linkedin.com/company/maneuver-hq)
