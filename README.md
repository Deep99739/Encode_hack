# 🌅 Equinox - Your AI-Powered Life OS

<div align="center">

**Balance your health, productivity, and focus with one intelligent platform**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-equinox0.netlify.app-blue?style=for-the-badge)](https://equinox0.netlify.app)
[![Built with Opik](https://img.shields.io/badge/📊_Observability-Opik-orange?style=for-the-badge)](https://www.comet.com/opik)
[![LangChain](https://img.shields.io/badge/🧠_AI-LangChain-green?style=for-the-badge)](https://langchain.com)

</div>

---

## 🎯 The Problem

Modern professionals are overwhelmed:
- **35+ apps switched daily** — health trackers, task managers, calendars, emails
- **No unified intelligence** — nothing connects your wellness with your productivity
- **Decision fatigue & burnout** — without a single source of truth, priorities slip through

## 💡 Our Solution

**Equinox** is an AI-powered life OS that unifies your health, tasks, and emails with multi-agent intelligence — fully traced using **Opik** for complete LLM observability.

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture
| Agent | Responsibility |
|-------|----------------|
| **Supervisor** | Routes queries to the appropriate specialist agent |
| **Wellness Agent** | Handles health, sleep, readiness, and workout queries |
| **Productivity Agent** | Manages emails, notes, todos, and calendar |
| **Briefing Agent** | Generates personalized morning summaries |

### 🌅 AI Morning Briefing
Wake up to a personalized summary:
- 🌙 Sleep Score (calculated from wellness data)
- 📧 Critical email count
- ✅ Today's task overview
- 💬 AI-generated motivational summary

### 💬 Agentic Chatbot
Natural language interface to manage your day:
```
"What are my tasks for today?"
"Do I have any critical emails?"
"How did I sleep last night?"
```

### 📊 Full Opik Observability
Every AI agent call is traced with **Opik**:
- LLM prompts and responses
- Latency and token usage
- Tool calls and agent decisions
- Conversation threading by `thread_id`

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python API |
| **LangChain + LangGraph** | Multi-agent orchestration |
| **Groq (Llama 3.3 70B)** | Fast LLM inference |
| **PostgreSQL** | Persistent data storage |
| **Opik** | LLM observability & tracing |
| **Google OAuth 2.0** | Gmail & Tasks integration |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19 + TypeScript** | Modern UI framework |
| **Vite** | Fast build tooling |
| **React Router** | Client-side navigation |
| **React Markdown (GFM)** | Rich chat rendering |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL database
- API Keys:
  - [Groq API](https://console.groq.com/keys)
  - [Opik API](https://www.comet.com/opik)
  - [Google OAuth Credentials](https://console.cloud.google.com/)

### One-Command Startup

```bash
# Clone the repository
git clone https://github.com/Deep99739/equinox.git
cd equinox

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Run everything
chmod +x startup.sh
./startup.sh
```

### Environment Variables

Create `backend/.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/equinox

# Opik Observability (Required for tracing)
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_opik_workspace
OPIK_PROJECT_NAME=equinox

# Google OAuth (for Gmail & Tasks)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

---

## 📁 Project Structure

```
equinox/
├── backend/
│   ├── agents/
│   │   ├── briefing/        # Morning briefing agent
│   │   ├── productivity/    # Email, notes, todos agent
│   │   └── wellness/        # Health and fitness agent
│   ├── supervisor/          # Query router (LangGraph)
│   ├── api/                 # REST endpoints
│   │   ├── briefing.py      # Briefing generation
│   │   ├── todos.py         # Task management
│   │   ├── notes.py         # Note-taking
│   │   └── google_oauth.py  # OAuth flow
│   ├── database/            # SQLAlchemy models
│   ├── state/               # User token management
│   ├── tools/               # Google API utilities
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home/        # Landing page
│   │   │   ├── Chat/        # Agentic chatbot
│   │   │   ├── Briefing/    # Morning briefing
│   │   │   ├── Productivity/# Notes & Todos
│   │   │   └── Wellness/    # Health dashboard
│   │   ├── components/      # Shared UI components
│   │   └── api/             # API client utilities
│   └── package.json
└── startup.sh               # Development startup script
```

---

## 🔌 API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ping` | Health check |
| `POST` | `/supervisor` | Send message to AI supervisor |

### Briefing
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/briefing/generate` | Generate morning briefing |
| `POST` | `/api/briefing/send-email` | Email briefing to user |

### Todos
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos/{email}` | Get user todos (Local + Google Tasks) |
| `POST` | `/todos/` | Create todo |
| `PATCH` | `/todos/{id}` | Toggle/update todo |
| `DELETE` | `/todos/{id}` | Delete todo |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/notes/{email}` | Get user notes |
| `POST` | `/notes/` | Create note |
| `PATCH` | `/notes/{id}` | Update note |
| `DELETE` | `/notes/{id}` | Delete note |

### Chat History
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/history/{email}` | Get all conversation threads |
| `GET` | `/api/history/{email}/{thread_id}` | Get specific thread |
| `POST` | `/api/history/{email}/{thread_id}` | Save thread |

---

## 📊 Opik Integration

Equinox uses **Opik** for complete LLM observability:

### What's Traced
- ✅ All LangChain agent invocations
- ✅ Tool calls (Gmail, Tasks, Notes)
- ✅ LLM prompts and responses
- ✅ Latency and token usage
- ✅ Conversation threading

### Viewing Traces
1. Go to [comet.com/opik](https://www.comet.com/opik)
2. Navigate to the `equinox` project
3. View traces grouped by `thread_id`

### Why Opik?
- **Debug AI issues** — See exactly what the LLM received and responded
- **Optimize costs** — Monitor token usage across agents
- **Improve quality** — Analyze agent decisions and tool usage

---

## 🧪 Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPIK_API_KEY not found` | Set in `backend/.env` |
| Google OAuth errors | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` |
| Rate limiting (429) | Groq free tier: 30 req/min. Wait or upgrade. |
| Database connection errors | Verify `DATABASE_URL` and PostgreSQL is running |
| Briefing shows 0 emails/tasks | Re-authenticate with Google OAuth |

---

## 👨‍💻 Author

**Deepak Kumar**

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**🌅 Equinox — Balance your day with AI**

*Built with ❤️ for the Opik Hackathon*

</div>
