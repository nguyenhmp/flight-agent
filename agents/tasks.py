from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any

@dataclass
class Task:
    role: Literal["backend", "frontend"]
    title: str
    goal: str
    acceptance: str
    hints: Optional[str] = None
    files_to_touch: Optional[list[str]] = None
    test_cmd: Optional[str] = None

# Library of common tasks
IMPLEMENT_CORS = Task(
    role="backend",
    title="Enable CORS on FastAPI",
    goal="Allow http://localhost:5173 to access the API.",
    acceptance="Preflight OPTIONS works and all endpoints accept cross-origin requests from the dev server.",
    files_to_touch=["app/main.py"],
)

CREATE_WATCHES_UI = Task(
    role="frontend",
    title="Create Watch form & list",
    goal="React page to POST /watch and GET /watch; show typical delta badges if present.",
    acceptance="User can add a watch and see it in the list without reload.",
    files_to_touch=["web/src/pages/Watches.tsx"],
)

FIX_MODERN_UNION_OPERATOR = Task(
    role="backend",
    title="Fix all type errors using float | None",
    goal="Make sure to fix all type errors like this unsupported operand type(s) for |: 'type' and 'NoneType'",
    acceptance="User can run uvicorn app.main:app --reload",
    files_to_touch=[],
)
