# Simple CLI to run agent tasks
import argparse, json
from agents.tasks import IMPLEMENT_CORS, CREATE_WATCHES_UI
from orchestrator.graph import run_task
import subprocess, os

TASKS = {
    "backend:cors": IMPLEMENT_CORS,
    "frontend:watches": CREATE_WATCHES_UI,
}


def auto_commit_push(msg="Agent commit"):
    subprocess.run("git add .", shell=True)
    subprocess.run(f'git commit -m "{msg}" || true', shell=True)
    subprocess.run("git push origin main", shell=True)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS.keys())
    args = parser.parse_args()
    result = run_task(TASKS[args.task])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
