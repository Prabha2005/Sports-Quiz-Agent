from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import v1_router
from app.database.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to initialize database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="Agentic AI Sports Quiz Platform API",
    description="Production-oriented REST API orchestrating a multi-agent LangGraph workflow for AI sports research, quiz generation, and SQLAlchemy persistence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend and clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(v1_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Service health verification endpoint."""
    return {
        "status": "healthy",
        "service": "Agentic AI Sports Quiz Platform",
        "version": "1.0.0"
    }
