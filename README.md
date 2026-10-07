# 🏆 Agentic AI Sports Research & Quiz Platform

An AI-powered Sports Research and Quiz Platform featuring a **stateful multi-agent orchestration engine (LangGraph)**, **asynchronous REST API (FastAPI)**, **strict data contracts (Pydantic v2)**, **relational database persistence (SQLAlchemy 2.0 + SQLite)**, and **dynamic knowledge retrieval (ChromaDB Vector RAG + DuckDuckGo Live Search)** with a decoupled **Streamlit** user interface.

---

## 🚀 Live Demo & Links

- **🌐 Live App:** https://sports-quiz-agent-xdk87zptk4yshbtdsnmqea.streamlit.app/
- **💻 GitHub Repository:** https://github.com/Prabha2005/Sports-Quiz-Agent

---

## 📌 Architecture & System Flow

The platform separates user interface presentation, HTTP routing, agentic reasoning, and database persistence into decoupled layers:

```text
Streamlit Frontend (port 8501)
    │
    │  HTTP / REST (httpx)
    ▼
FastAPI Backend (port 8000)
    │
    │  Dependency Injection (Async Router -> QuizService -> LangGraph)
    ▼
LangGraph Multi-Agent Engine
    │
    ├──> 1. research_node (ChromaDB Vector Retrieval + DuckDuckGo Live News)
    │
    ├──> 2. generate_node (LangChain + Gemini with typed QuizOutput schema)
    │
    └──> 3. validate_node (Fact-checking & quality score in [0.0, 1.0])
          │
          ├── [is_valid == True] ─────────► save_node (Mark validated)
          │                                      │
          ├── [is_valid == False & retry < 3] ──► generate_node (Critique injection)
          │
          └── [is_valid == False & retry >= 3] ─► error_node (HTTP 422, zero DB writes)
                                                 │
                                                 ▼
                                     SQLAlchemy 2.0 ORM Layer
                                                 │
                                                 ▼
                                     SQLite Database (sports_quiz.db)
```

---

## ✨ Key Features

- 🧠 **Multi-Agent Cyclic Orchestration (LangGraph):** Self-correcting generation loop with automated validation, critique feedback injection, and bounded retries.
- ⚡ **Asynchronous REST API (FastAPI):** High-performance endpoints (`/api/v1/quizzes/generate`, `/api/v1/quizzes/{id}`, `/api/v1/attempts/submit`, `/health`) with dependency injection and interactive OpenAPI documentation.
- 🔒 **Strict Data Contracts (Pydantic v2):** Enforces rigid schemas (exactly 4 questions, options `A/B/C/D`, validated answer keys, bounded scores).
- 📚 **Hybrid Retrieval (RAG + Live Search):** Combines static historical domain facts from ChromaDB with real-time web search from DuckDuckGo.
- 💾 **Relational Persistence (SQLAlchemy 2.0 + SQLite):** Stores quizzes, questions, and scored user attempts with foreign-key relationships and cascade deletion.
- 🎨 **Decoupled Streamlit Frontend:** Clean UI communicating exclusively over HTTP via a dedicated `APIClient`.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language & OOP** | Python 3.11 | Core object-oriented service layer |
| **Agentic Workflow** | LangGraph | Stateful cyclic graph & self-correction retry loops |
| **LLM & Prompts** | LangChain & Google Gemini API | Prompt templates & structured output bindings |
| **REST API** | FastAPI & Uvicorn | Async HTTP backend, routing, OpenAPI docs |
| **Data Validation** | Pydantic v2 | Strict DTO schemas and LLM output parsing |
| **Vector Database** | ChromaDB & Sentence Transformers | RAG historical sports knowledge retrieval |
| **Live Web Search** | DuckDuckGo (`ddgs`) | Real-time sports news and tournament updates |
| **Database & ORM** | SQLAlchemy 2.0 & SQLite | Relational models (`Quiz`, `Question`, `QuizAttempt`) |
| **Frontend UI** | Streamlit & `httpx` | Decoupled user interface & HTTP API client |

---

## 📂 Project Structure

```text
sports-quiz-agent/
│
├── app/                               # Production Application Package
│   ├── main.py                        # FastAPI entrypoint, CORS, OpenAPI router
│   ├── api/                           # REST API Endpoints & Dependency Injection
│   │   ├── deps.py                    # Database & Service dependencies
│   │   └── v1/
│   │       ├── quizzes.py             # Quiz generation & retrieval endpoints
│   │       └── attempts.py            # Quiz attempt submission & scoring
│   ├── database/                      # SQLAlchemy Database Session & Base
│   │   ├── base.py                    # DeclarativeBase model registry
│   │   └── session.py                 # SQLite engine & session factory
│   ├── models/                        # SQLAlchemy ORM Models
│   │   ├── quiz.py                    # Quiz & Question models
│   │   └── attempt.py                 # QuizAttempt model
│   ├── schemas/                       # Pydantic v2 Schemas & Contracts
│   │   ├── quiz.py                    # QuizOutput, QuestionItem, ValidationResult
│   │   └── attempt.py                 # SubmitAttemptRequest, AttemptResultResponse
│   ├── prompts/                       # LangChain ChatPromptTemplates
│   │   ├── quiz_prompt.py             # Generation prompt template
│   │   └── validation_prompt.py       # Fact-checking & validation prompt
│   ├── services/                      # Modular OOP Service Layer
│   │   ├── rag_service.py             # ChromaDB vector retrieval service
│   │   ├── search_service.py          # DuckDuckGo search service
│   │   ├── llm_service.py             # Gemini client with fallback & structured output
│   │   └── quiz_service.py            # Database CRUD & attempt scoring service
│   └── graph/                         # LangGraph Multi-Agent Engine
│       ├── state.py                   # AgentState definition
│       ├── nodes.py                   # research, generate, validate, save, error nodes
│       └── workflow.py                # Stateful cyclic graph compiler
│
├── frontend/                          # Decoupled Streamlit Frontend Package
│   ├── streamlit_app.py               # Main UI with session state management
│   ├── api_client.py                  # HTTP client (httpx) calling FastAPI
│   └── components/                    # Modular UI components
│       ├── quiz_view.py               # 4-question interactive form
│       └── result_view.py             # Scorecard, breakdown & explanations
│
├── src/                               # Baseline Procedural Prototype (Preserved)
│   ├── config.py
│   ├── database.py
│   ├── generator.py
│   └── search.py
│
├── app.py                             # Legacy Synchronous Streamlit Entrypoint
├── run_app.py                         # Unified Application Runner
├── requirements.txt                   # Project Dependencies
├── .env.example                       # Environment template
└── README.md
```

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Prabha2005/Sports-Quiz-Agent.git
cd sports-quiz-agent
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

---

## ▶️ Running the Application

### Option A: Run the Multi-Agent Platform (FastAPI + Decoupled UI)

To launch both the FastAPI backend (`port 8000`) and the Streamlit frontend (`port 8501`) together:

```bash
python run_app.py
```

Or run them in separate terminals:

```bash
# Terminal 1: FastAPI Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Streamlit Frontend
streamlit run frontend/streamlit_app.py
```

- **Interactive UI:** [http://localhost:8501](http://localhost:8501)
- **Interactive OpenAPI / Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Run the Legacy Synchronous Prototype (Baseline)

```bash
streamlit run app.py
```

---

## 🖼️ Screenshots

### Home Page
<img width="1917" height="917" alt="home" src="https://github.com/user-attachments/assets/3be0f754-4614-47e1-8502-2bf3e9459dd2" />

---

### Generated Quiz
<img width="1917" height="907" alt="quiz" src="https://github.com/user-attachments/assets/ae4e6f1e-4e13-4609-b300-7df54b252750" />

---

### Historical Facts
<img width="1917" height="907" alt="historical-facts" src="https://github.com/user-attachments/assets/e576bf39-8115-4970-8bca-b964b19447ec" />

---

### Latest Sports News
<img width="1917" height="912" alt="latest-news" src="https://github.com/user-attachments/assets/1c172850-9fd2-4139-a72f-e9f08808a2c1" />

---

## 🎯 Key Technical Capabilities Demonstrated

- **Agentic AI & Self-Correction:** Cyclic graph with critique injection and validation loops.
- **Strict Structured Outputs:** Native Pydantic schema parsing via `with_structured_output()`.
- **Decoupled Microservice Architecture:** HTTP REST API boundary separating UI from LLM orchestration.
- **Relational Data Modeling:** SQLAlchemy 2.0 ORM, foreign keys, cascade deletes, atomic commits.
- **Hybrid Context Gathering:** ChromaDB vector embeddings + DuckDuckGo live news search.