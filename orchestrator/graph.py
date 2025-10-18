# Minimal multi-agent orchestrator (LLM-optional).
import os, pathlib, json, time
from typing import Callable, Dict, Any

# Fix the ImportError by adding the project root to the system path
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Now imports resolve correctly from the root
from agents.tasks import Task
from agents import tools

def _llm_complete(system: str, user: str) -> str:
    """Uses the configured LLM API (Gemini or OpenAI) to generate the code proposal."""
    
    # 1. Check for Gemini Key and prioritize it
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

            # Gemini System Instruction and structured prompt
            full_prompt = (
                f"You are a professional software engineer. Follow the System Charter and complete the User Task below. "
                f"You must output only the raw, runnable code for the files requested, without any conversational preamble, explanation, or markdown wrappers (like ```python). "
                f"If the task requires a change to an existing file, provide only the necessary functions or code blocks that need to be added or replaced. \n\n"
                f"SYSTEM CHARTER:\n{system}\n\nUSER TASK:\n{user}"
            )

            rsp = client.models.generate_content(
                model=model_name,
                contents=[full_prompt],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    system_instruction="You are a pair programming AI. Your output must be only code and nothing else.",
                )
            )
            return rsp.text
        except ImportError:
            return "// ERROR: GEMINI_API_KEY set, but 'google-genai' package is not installed. Run 'pip install google-genai'."
        except Exception as e:
            return f"// LLM error (Gemini): {e}\n"

    # 2. Check for OpenAI Key as a fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            # OpenAI System and User messages
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]

            rsp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2
            )
            return rsp.choices[0].message.content or ""
        except ImportError:
            return "// ERROR: OPENAI_API_KEY set, but 'openai' package is not installed. Run 'pip install openai'."
        except Exception as e:
            return f"// LLM error (OpenAI): {e}\n"

    # 3. No key found
    return f"""// NO API KEY SET.
// Please set either the GEMINI_API_KEY (preferred) or OPENAI_API_KEY environment variable.
// System:
{system}
// User Task:
{user}
// TODO: Implement manually.
"""

def run_task(task: Task) -> Dict[str, Any]:
    if task.role == "backend":
        system = (ROOT / "agents" / "backend_agent.md").read_text()
    else:
        system = (ROOT / "agents" / "frontend_agent.md").read_text()

    # Use tools.list_repo() to give the model context of the whole project
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
