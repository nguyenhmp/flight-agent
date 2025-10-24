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
    goal="Make sure to fix all \"TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\" errors across the repository",
    acceptance="User can run uvicorn app.main:app --reload",
    files_to_touch=[],
)

WRITE_WATCHES_PAGE_VITEST_TESTS = Task(
    role="frontend",
    title="Write Vitest tests for the Watches page",
    goal="Create comprehensive Vitest tests for the Watches page to ensure its functionality and UI elements are working correctly.",
    acceptance="All major components and functions of the Watches page have passing Vitest tests, including form submission, data fetching, and display of watch data.",
    files_to_touch=["web/src/pages/Watches.tsx", "web/src/pages/Watches.test.tsx"],
)

SETUP_WEB_DEPENDENCIES = Task(
    role="frontend",
    title="Set up web dependencies and start command",
    goal="Ensure the web project has all necessary dependencies and a command to start the front end server.",
    acceptance="The web project can be started with `npm run dev` and the frontend is accessible in the browser.",
    files_to_touch=["web/package.json"],
    test_cmd="npm run dev",
)

SETUP_REACT_ROOT = Task(
    role="frontend",
    title="Set up React root in index.html",
    goal="Configure the front end server to serve an index.html file with a React root element.",
    acceptance="The index.html file exists and contains a div with id 'root', and the React application is correctly mounted to this root element.",
    files_to_touch=["web/index.html", "web/src/main.tsx"],
)

FIX_APP_IMPORT = Task(
    role="frontend",
    title="Fix App import in src/main.tsx",
    goal="Resolve the import error 'Failed to resolve import ./App from src/main.tsx'.",
    acceptance="The React application compiles and runs without import errors.",
    files_to_touch=["web/src/main.tsx"],
)

REFACTOR_WATCHES_PAGE_TO_FLIGHTS = Task(
    role="frontend",
    title="Refactor Watches page to Flights page",
    goal="Update the Watches page to track flights instead of wrist watches. This includes renaming components, updating form fields, and adjusting data fetching to reflect flight information.",
    acceptance="The page now displays flight tracking information, with the ability to add and view flights. All UI elements and data reflect flight details.",
    files_to_touch=["web/src/pages/Watches.tsx", "web/src/pages/Watches.test.tsx"],
)