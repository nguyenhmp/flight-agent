# Simple CLI to run agent tasks
import argparse, json
import pathlib
import sys
import os
from dotenv import load_dotenv # Import the dotenv library

# Load environment variables from .env file immediately
load_dotenv() 

# Fix the ModuleNotFoundError by adding the project root to the system path
# We must do this before trying to import project modules like 'agents'
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from agents.tasks import IMPLEMENT_CORS, CREATE_WATCHES_UI, FIX_MODERN_UNION_OPERATOR, WRITE_WATCHES_PAGE_VITEST_TESTS, SETUP_WEB_DEPENDENCIES, SETUP_REACT_ROOT, FIX_APP_IMPORT, REFACTOR_WATCHES_PAGE_TO_FLIGHTS, ADD_BASIC_CSS_STYLING, CONFIGURE_TAILWIND, INSTALL_TAILWIND_POSTCSS
from orchestrator.graph import run_task

TASKS = {
    "backend:cors": IMPLEMENT_CORS,
    "frontend:watches": CREATE_WATCHES_UI,
    "backend:type-fix": FIX_MODERN_UNION_OPERATOR,
    "frontend:write-watches-page-vitest-tests": WRITE_WATCHES_PAGE_VITEST_TESTS,
    "backend:implement-cors": IMPLEMENT_CORS,
    "frontend:setup-web-dependencies": SETUP_WEB_DEPENDENCIES,
    "frontend:setup-react-root": SETUP_REACT_ROOT,
    "frontend:fix-app-import": FIX_APP_IMPORT,
    "frontend:refactor-watches-page-to-flights": REFACTOR_WATCHES_PAGE_TO_FLIGHTS,
    "frontend:add-basic-css-styling": ADD_BASIC_CSS_STYLING,
    "frontend:configure-tailwind": CONFIGURE_TAILWIND,
    "frontend:install-tailwind-postcss": INSTALL_TAILWIND_POSTCSS,

}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS.keys())
    args = parser.parse_args()
    result = run_task(TASKS[args.task])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
