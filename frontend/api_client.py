import os
from typing import Dict, Any, Optional
import httpx


class APIClient:
    """HTTP Client communicating exclusively with the FastAPI REST backend."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 90.0):
        raw_url = base_url or os.getenv("API_BASE_URL") or "http://127.0.0.1:8000"
        self.base_url = raw_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """Checks if the FastAPI backend is running and healthy."""
        try:
            with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
                res = client.get("/health")
                if res.status_code == 200:
                    return {"connected": True, "data": res.json()}
                return {"connected": False, "error": f"Status {res.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def generate_quiz(
        self,
        sport: str,
        difficulty: str = "Medium",
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calls POST /api/v1/quizzes/generate to run the multi-agent LangGraph workflow.
        Returns a dict with 'success': True, 'data': {...} or 'success': False, 'error': '...'.
        """
        payload = {
            "sport": sport,
            "difficulty": difficulty,
            "topic": topic if topic and topic.strip() else None
        }

        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                res = client.post("/api/v1/quizzes/generate", json=payload)

                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                elif res.status_code == 422:
                    error_detail = res.json().get("detail", "Validation failed during generation.")
                    return {"success": False, "error": f"Generation Rejected: {error_detail}"}
                else:
                    return {"success": False, "error": f"Server returned HTTP {res.status_code}: {res.text}"}
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Could not connect to FastAPI backend at " + self.base_url + ". Ensure 'uvicorn app.main:app' is running."
            }
        except httpx.TimeoutException:
            return {"success": False, "error": "Request timed out while waiting for multi-agent graph."}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def get_quiz(self, quiz_id: str) -> Dict[str, Any]:
        """
        Calls GET /api/v1/quizzes/{quiz_id} to retrieve a persisted quiz from SQLite.
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=10.0) as client:
                res = client.get(f"/api/v1/quizzes/{quiz_id}")
                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                elif res.status_code == 404:
                    return {"success": False, "error": f"Quiz with ID '{quiz_id}' was not found in SQLite."}
                else:
                    return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def submit_attempt(
        self,
        quiz_id: str,
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Calls POST /api/v1/attempts/submit to score user answers and persist the attempt.
        """
        payload = {
            "quiz_id": quiz_id,
            "answers": answers
        }

        try:
            with httpx.Client(base_url=self.base_url, timeout=10.0) as client:
                res = client.post("/api/v1/attempts/submit", json=payload)
                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                elif res.status_code == 404:
                    return {"success": False, "error": f"Quiz with ID '{quiz_id}' was not found."}
                else:
                    return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
