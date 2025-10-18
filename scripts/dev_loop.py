# Simple CLI to run agent tasks
import argparse, json
from agents.tasks import IMPLEMENT_CORS, CREATE_WATCHES_UI
from orchestrator.graph import run_task

TASKS = {
    "backend:cors": IMPLEMENT_CORS,
    "frontend:watches": CREATE_WATCHES_UI,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS.keys())
    args = parser.parse_args()
    result = run_task(TASKS[args.task])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
