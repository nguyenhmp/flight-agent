# Minimal multi-agent orchestrator (LLM-optional).
# You can plug in OpenAI by setting OPENAI_API_KEY; otherwise it will create TODOs instead of code.
import os, pathlib, json, time
from typing import Callable, Dict, Any
from agents.tasks import Task
from agents import tools

ROOT = pathlib.Path(__file__).resolve().parents[1]

def _llm_complete(system: str, user: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # No LLM configured; return a TODO block to be helpful.
        return f"""// OPENAI_API_KEY not set.
// System:
{system}
// User Task:
{user}
// TODO: Implement manually.
"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        rsp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.2
        )
        return rsp.choices[0].message.content or ""
    except Exception as e:
        return f"// LLM error: {e}\n"

def run_task(task: Task) -> Dict[str, Any]:
    if task.role == "backend":
        system = (ROOT / "agents" / "backend_agent.md").read_text()
    else:
        system = (ROOT / "agents" / "frontend_agent.md").read_text()

    user = f"Title: {task.title}\nGoal: {task.goal}\nAcceptance: {task.acceptance}\nFiles: {task.files_to_touch or []}\nProject tree: {tools.list_repo()}"
    proposal = _llm_complete(system, user)

    # naive: if it looks like code + file path hints, write to files listed
    changes = []
    if task.files_to_touch:
        for path in task.files_to_touch:
            # append or create with proposal
            prev = ""
            try:
                prev = tools.read_file(path)
            except FileNotFoundError:
                prev = ""
            new_content = f"""{prev}\n\n/* --- Agent change: {task.title} --- */\n{proposal}\n"""
            changes.append(tools.write_file(path, new_content))
    return {"proposal": proposal, "changes": changes}
