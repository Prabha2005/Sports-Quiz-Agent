from fastapi import APIRouter
from app.api.v1.quizzes import router as quizzes_router
from app.api.v1.attempts import router as attempts_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(quizzes_router)
v1_router.include_router(attempts_router)
