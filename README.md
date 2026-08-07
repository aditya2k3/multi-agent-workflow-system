## Complete `README.md` File — Copy & Save

Since I can't create downloadable files directly, here's the complete README content. **Copy everything below → paste into a new file named `README.md`** in your project root.

```markdown
# 🤖 Multi-Agent Enterprise AI Workflow System

An intelligent multi-agent AI platform that routes user requests to specialized agents for meeting analysis, document processing, business research, calendar scheduling, and email automation — powered by DeepSeek AI with real Google Workspace integration.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [API Keys Setup](#-api-keys-setup)
- [Google OAuth Setup](#-google-oauth-setup)
- [Running the App](#-running-the-app)
- [Docker Deployment](#-docker-deployment)
- [API Endpoints](#-api-endpoints)
- [Example Prompts](#-example-prompts)
- [Database Schema](#-database-schema)
- [How the Router Works](#-how-the-router-works)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🌟 Overview

This system is a **true multi-agent AI assistant**. Instead of one chatbot trying to do everything, a central **Router Agent** classifies every user message and dispatches it to the correct specialized agent. Each agent has **tool access** — it can call real Google APIs, search the web, and read/write to a SQLite database for persistent memory.

```
User: "Schedule a meeting with john@company.com on Friday at 2pm"
        ↓
Router Agent (DeepSeek) → classifies intent as "schedule"
        ↓
Scheduler Agent
  1. Parses natural language → structured JSON (DeepSeek)
  2. Creates real Google Calendar event (Calendar API)
  3. Sends invitation email to attendees (Gmail API)
  4. Saves event to database (SQLite)
        ↓
✅ Confirmation with calendar link returned to user
```

---

## ✨ Features

| Agent | Capability | Real Integrations |
|---|---|---|
| 🧠 **Router Agent** | Auto-detects intent, routes to correct agent | DeepSeek AI |
| 📋 **Meeting Agent** | Summarizes transcripts, extracts action items, decisions, sentiment | DeepSeek AI |
| 📄 **Upload Agent** | Analyzes PDF / TXT / CSV files, extracts insights | DeepSeek + PyPDF2 |
| 🔍 **Research Agent** | Web search + business intelligence reports | Tavily API + DeepSeek |
| 📅 **Schedule Agent** | Creates real calendar events from natural language | Google Calendar + Gmail |
| 📧 **Email Agent** | Drafts and sends real emails from your Gmail | Gmail API |
| 🗄️ **History Agent** | Reads past events, emails, research from database | SQLite |

### Additional Highlights

- 💬 ChatGPT-style dark UI with full markdown rendering (tables, headers, lists)
- 🎯 Intent badges showing which agent handled each request
- 📎 File upload with attachment indicator
- 🔒 OAuth2 secure Google login (one-time)
- 🐳 Fully containerized with Docker
- 🗄️ Persistent memory — all actions saved to SQLite

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              FRONTEND (index.html)                   │
│   Chat UI • Markdown Renderer • File Upload         │
└──────────────────────┬──────────────────────────────┘
                       │ POST /router/chat
                       ▼
┌─────────────────────────────────────────────────────┐
│              ROUTER AGENT (DeepSeek)                 │
│         Classifies intent into 7 categories         │
└──┬──────┬──────┬────────┬────────┬──────┬──────────┘
   ▼      ▼      ▼        ▼        ▼      ▼
Meeting Upload Research Schedule Email  History
Agent   Agent  Agent    Agent    Agent  (DB Read)
   │      │      │        │        │      │
   ▼      ▼      ▼        ▼        ▼      ▼
DeepSeek DeepSeek Tavily+ Google   Gmail  SQLite
         +PyPDF2 DeepSeek Calendar  API   Database
                          +Gmail
                            │
                            ▼
                 ┌─────────────────────┐
                 │   SQLite DATABASE    │
                 │  (Tool Access Layer) │
                 │  All agents can      │
                 │  read & write        │
                 └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn |
| AI Engine | DeepSeek-V4-Flash via Hugging Face Inference API |
| Web Search | Tavily Search API |
| Calendar | Google Calendar API (OAuth2) |
| Email | Gmail API (OAuth2) |
| Database | SQLite + SQLAlchemy ORM |
| PDF Parsing | PyPDF2 |
| Frontend | HTML + CSS + Vanilla JavaScript |
| Icons | Phosphor Icons |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
Multi Agent Workflow System/
│
├── Backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   │
│   ├── api/                       # API route layer
│   │   ├── __init__.py
│   │   ├── router.py              # Main router endpoint
│   │   ├── meetings.py            # Meeting agent endpoint
│   │   ├── upload.py              # File upload endpoint
│   │   ├── analysis.py            # Research endpoint
│   │   ├── schedule.py            # Schedule endpoint
│   │   ├── email.py               # Email endpoint
│   │   └── history.py             # Database history endpoints
│   │
│   ├── agents/                    # Agent logic layer
│   │   ├── __init__.py
│   │   ├── router.py              # Intent classification + routing
│   │   ├── meeting_agent.py
│   │   ├── upload_agent.py
│   │   ├── research_agent.py
│   │   ├── scheduler_agent.py
│   │   └── email_agent.py
│   │
│   ├── prompts/                   # Prompt templates
│   │   ├── __init__.py
│   │   ├── router_prompt.py
│   │   ├── meeting_prompt.py
│   │   ├── upload_prompt.py
│   │   ├── research_prompt.py
│   │   ├── schedule_prompt.py
│   │   └── email_prompt.py
│   │
│   ├── services/                  # External API integrations
│   │   ├── __init__.py
│   │   ├── gemini_service.py      # DeepSeek via Hugging Face
│   │   ├── tavily_service.py      # Tavily web search
│   │   ├── google_auth_service.py # OAuth2 authentication
│   │   ├── calendar_service.py    # Google Calendar API
│   │   └── gmail_service.py       # Gmail API
│   │
│   ├── tools/                     # Tool access layer
│   │   ├── __init__.py
│   │   └── agent_tools.py         # DB + API tool wrappers
│   │
│   ├── database/                  # Database layer
│   │   ├── __init__.py
│   │   ├── database.py            # Engine + session setup
│   │   ├── models.py              # 6 ORM table models
│   │   └── crud.py                # CRUD + agent loggers
│   │
│   └── config/                    # Configuration
│       ├── __init__.py
│       ├── settings.py            # Environment variables
│       ├── credentials.json       # Google OAuth (DO NOT COMMIT)
│       └── token.json             # Auth token (DO NOT COMMIT)
│
├── frontend/
│   └── index.html                 # Complete chat UI
│
├── storage/                       # Uploaded files
│   ├── pdf/
│   └── temp/
│
├── .env                           # API keys (DO NOT COMMIT)
├── .gitignore                     # Protects secrets
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── enterprise.db                  # SQLite database (auto-created)
└── README.md
```

---

## 🔧 Prerequisites

| Requirement | Version | Download |
|---|---|---|
| Python | 3.10+ | https://python.org |
| Docker Desktop | Latest | https://docker.com |
| Git | Latest | https://git-scm.com |
| Google Account | — | For Calendar + Gmail |
| Hugging Face Account | — | https://huggingface.co |
| Tavily Account | — | https://tavily.com |

---

## 🚀 Installation

### 1. Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/Multi-Agent-Workflow-System.git
cd "Multi Agent Workflow System"
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create Required Folders

```powershell
mkdir storage\pdf
mkdir storage\temp
```

---

## 🔑 API Keys Setup

### Create `.env` File (Project Root)

```env
HF_TOKEN=hf_your_huggingface_token_here
TAVILY_API_KEY=tvly-your_tavily_key_here
GOOGLE_API_KEY=your_gemini_key_here
```

### Where to Get Each Key

| Key | Where to Get | Free Tier |
|---|---|---|
| `HF_TOKEN` | https://huggingface.co/settings/tokens → Create token (Read) | ✅ Unlimited |
| `TAVILY_API_KEY` | https://tavily.com → Dashboard → API Keys | ✅ 1000 searches/month |
| `GOOGLE_API_KEY` | https://aistudio.google.com/apikey | ✅ Optional (backup) |

---

## 🔐 Google OAuth Setup (Calendar + Gmail)

This enables **real** calendar events and email sending from your Gmail.

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click **"Create Project"** → Name: `Enterprise AI Assistant`

### Step 2: Enable APIs

Enable these two APIs:
- **Google Calendar API**: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
- **Gmail API**: https://console.cloud.google.com/apis/library/gmail.googleapis.com

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services → OAuth Consent Screen**
2. User Type: **External**
3. App Name: `Enterprise AI Assistant`
4. Add your email as **Test User**
5. Add Scopes:
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/gmail.send`

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth Client ID**
3. Application Type: **Desktop App**
4. Download the JSON file
5. Save it as: `Backend/config/credentials.json`

### Step 5: First Login

When you first schedule an event or send an email, a browser window opens:
1. Sign in with your Gmail
2. Grant permissions
3. Token is saved to `Backend/config/token.json`
4. **You never need to login again** ✅

---

## ▶️ Running the App

### Local Development

```powershell
uvicorn Backend.main:app --reload
```

Open: **http://127.0.0.1:8000**

### Verify All Endpoints

Open: **http://127.0.0.1:8000/docs** — Interactive API documentation (Swagger UI)

---

## 🐳 Docker Deployment

### Build & Run

```powershell
docker compose up --build
```

### Run in Background

```powershell
docker compose up -d
```

### View Logs

```powershell
docker compose logs -f
```

### Stop

```powershell
docker compose down
```

### Rebuild After Code Changes

```powershell
docker compose up --build
```

---

## 📡 API Endpoints

### Main Router (Recommended — Auto-Detects Intent)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/router/chat` | Send any message — router auto-routes |
| POST | `/router/chat-with-file` | Send message + file attachment |

### Individual Agents (Direct Access)

| Method | Endpoint | Agent |
|---|---|---|
| POST | `/meeting/chat` | Meeting Agent |
| POST | `/upload/analyze` | Upload Agent |
| POST | `/analysis/research` | Research Agent |
| POST | `/schedule/create` | Schedule Agent |
| POST | `/email/send` | Email Agent |

### Database History (Read)

| Method | Endpoint | Returns |
|---|---|---|
| GET | `/history/chat?limit=50` | Chat messages |
| GET | `/history/events?limit=50` | Scheduled events |
| GET | `/history/emails?limit=50` | Sent emails |
| GET | `/history/research?limit=50` | Research queries |
| GET | `/history/meetings?limit=50` | Meeting analyses |
| GET | `/history/files?limit=50` | Uploaded files |

### Request/Response Format

**Request (Router):**
```json
{
  "query": "Schedule a meeting with john@company.com on Friday at 2pm"
}
```

**Response:**
```json
{
  "response": "✅ EVENT CREATED SUCCESSFULLY\n\n📅 Title: Meeting...",
  "intent": "schedule"
}
```

---

## 💬 Example Prompts

### Meeting Agent
```
Summarize this meeting: John said we need to launch by Q3. 
Sarah will handle marketing. Budget is $50K.
```

### Upload Agent
```
[Attach PDF] → Extract key clauses from this contract
```

### Research Agent
```
Research Q3 2025 SaaS market trends and competitor analysis
```

### Schedule Agent
```
Schedule a product review with john@company.com and 
sarah@company.com on Friday at 2pm for 45 minutes in Conference Room A
```

### Email Agent
```
Write a formal email to boss@company.com requesting 
next week off for a family event
```

### History Agent (Database Read)
```
Show my scheduled events
Show my sent emails
What research did I do yesterday?
What's in the database?
```

---

## 🗄️ Database Schema

The system uses **SQLite** with 6 tables:

| Table | Purpose | Key Fields |
|---|---|---|
| `chat_messages` | All conversations | role, content, intent, created_at |
| `scheduled_events` | Calendar events | title, date, time, attendees, calendar_link |
| `sent_emails` | Sent emails | to_emails, subject, body, status, message_id |
| `research_history` | Research queries | query, result, created_at |
| `meeting_history` | Meeting analyses | query, result, task, created_at |
| `uploaded_files` | File uploads | filename, file_path, query, result |

### Tool Access Pattern

Every agent automatically logs its actions:

```python
# In scheduler_agent.py — after creating calendar event
from Backend.database.crud import log_event
log_event(
    title="Product Review",
    date="2025-08-08",
    time="14:00",
    duration_minutes=45,
    attendees="john@company.com, sarah@company.com",
    location="Conference Room A",
    calendar_link="https://calendar.google.com/event?eid=...",
    status="created",
)
```

Users can then query the database naturally:
```
User: "Show my scheduled events"
Router → intent: "history" → handle_history()
→ Reads from SQLite → Returns formatted list
```

---

## 🧠 How the Router Works

### Intent Classification

The router uses DeepSeek to classify every message into one of **7 categories**:

| Intent | Triggers |
|---|---|
| `meeting` | summarize, transcript, meeting notes, action items |
| `upload` | PDF, file, document, analyze, extract |
| `research` | research, trends, market, competitors, search |
| `schedule` | schedule, meeting, event, calendar, book |
| `email` | email, draft, send, compose, reply |
| `history` | show, list, my events, past, database |
| `chat` | greetings, general questions |

### Routing Flow

```python
def route_to_agent(user_input):
    # Step 1: Classify intent with DeepSeek
    intent = classify_intent(user_input)  # Returns: "schedule"
    
    # Step 2: Route to correct agent
    if intent == "schedule":
        response = run_scheduler_agent(user_input)
    elif intent == "email":
        response = run_email_agent(user_input)
    # ... etc
    
    # Step 3: Log to database
    log_chat("user", user_input, intent)
    log_chat("ai", response, intent)
    
    # Step 4: Return
    return {"response": response, "intent": intent}
```

---

## 🛠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'Backend'`

**Fix:** Make sure you have `__init__.py` in every folder:

```powershell
# Run from project root
New-Item Backend/__init__.py
New-Item Backend/api/__init__.py
New-Item Backend/agents/__init__.py
New-Item Backend/prompts/__init__.py
New-Item Backend/services/__init__.py
New-Item Backend/tools/__init__.py
New-Item Backend/database/__init__.py
New-Item Backend/config/__init__.py
```

### Issue: `429 RESOURCE_EXHAUSTED` (Gemini Rate Limit)

**Fix:** You're on Gemini free tier (20 requests/day). Switch to Hugging Face:

```python
# Backend/services/gemini_service.py
from huggingface_hub import InferenceClient
client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
```

### Issue: `404 NOT FOUND` on `/router/chat`

**Fix:** Router not registered in `main.py`. Add:

```python
from Backend.api.router import router as router_router
app.include_router(router_router)
```

### Issue: `Google Calendar API 403 Forbidden`

**Fix:** Regenerate OAuth token:

```powershell
# Delete old token
del Backend\config\token.json

# Restart app — browser opens for re-login
uvicorn Backend.main:app --reload
```

### Issue: Frontend shows raw markdown (`#`, `**`, `|`)

**Fix:** Hard refresh browser: **Ctrl + Shift + R**

### Issue: `AttributeError: 'list' object has no attribute 'strip'`

**Fix:** DeepSeek returns a list. Update `call_gemini()`:

```python
def call_gemini(prompt: str) -> str:
    response = model.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        return " ".join(str(block) for block in content)
    return str(content)
```

---

## 🗺️ Roadmap

| Feature | Status | Description |
|---|---|---|
| Multi-Agent Router | ✅ Done | Auto-detects intent, routes to correct agent |
| Meeting Agent | ✅ Done | Summarizes transcripts, extracts action items |
| Upload Agent | ✅ Done | PDF/TXT/CSV analysis with DeepSeek |
| Research Agent | ✅ Done | Tavily web search + DeepSeek analysis |
| Schedule Agent | ✅ Done | Google Calendar + Gmail invitations |
| Email Agent | ✅ Done | Draft + send via Gmail API |
| Database Layer | ✅ Done | SQLite with tool access for all agents |
| History Agent | ✅ Done | Natural language database queries |
| Docker Deployment | ✅ Done | Full containerization |
| Markdown Rendering | ✅ Done | Tables, headers, lists in chat UI |
| Voice Input | 🔲 Planned | Speech-to-text for hands-free use |
| Streaming Responses | 🔲 Planned | Word-by-word AI responses |
| User Authentication | 🔲 Planned | JWT login, multi-user support |
| PostgreSQL Migration | 🔲 Planned | Production-grade database |
| Mobile App | 🔲 Planned | React Native / Flutter client |

---

## 👤 Author

**Aditya Gupta**

- GitHub: [@aditya-rawat](https://github.com/aditya-rawat)
- Project: Multi-Agent Enterprise AI Workflow System

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **DeepSeek AI** — Powerful open-source LLM
- **Hugging Face** — Free inference API hosting
- **Tavily** — Web search API for AI agents
- **Google Workspace APIs** — Calendar + Gmail integration
- **FastAPI** — Modern Python web framework

---

⭐ **Star this repo if you found it helpful!**
```

---

## How to Save This File

### Method 1: VS Code

1. Open your project in VS Code
2. Click **New File** icon (or right-click → New File)
3. Name it: `README.md`
4. **Select all** the markdown code above (between the ``` markers)
5. **Copy** → **Paste** into the file
6. **Save** (Ctrl+S)

### Method 2: PowerShell

```powershell
# Creates README.md in current directory
New-Item -Path "README.md" -ItemType File
notepad README.md
# Paste the content → Save
```

---

## Then Push to GitHub

```powershell
git add README.md
git commit -m "Add comprehensive README documentation"
git push origin main
```

Your README will now display beautifully on your GitHub repository page! 🎉
