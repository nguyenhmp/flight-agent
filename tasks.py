import argparse
import pathlib
import sys
import os
import re
from dotenv import load_dotenv

# --- Load Environment & Fix Imports ---
ROOT = pathlib.Path(__file__).resolve().parent
dotenv_path = ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)
print(f"Loaded environment variables from: {dotenv_path}")

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from agents import tools
    # --- START FIX: Add direct LLM imports ---
    import google.generativeai as genai
    from openai import OpenAI
    # --- END FIX ---
except ImportError:
    print("❌ Error: Could not import 'agents' or 'genai'/'openai'.")
    print("Please run 'pip install -r requirements.txt'")
    sys.exit(1)

# --- End Setup ---


# --- START FIX: Add a local LLM function that asks for RAW CODE ---
def _llm_complete_raw(system: str, user: str) -> str:
    """Uses the configured LLM API to generate RAW CODE."""
    
    # 1. Check for Gemini Key and prioritize it
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            client = genai.GenerativeModel
            model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash") 

            # This is the system instruction from your PM_AGENT charter
            system_instruction_raw = (
                "You are a professional software engineer. "
                "You MUST output *only* the raw Python code for the new `Task` object. "
                "DO NOT include any conversation, explanation, or markdown wrappers."
            )

            model = client(
                model_name=model_name,
                system_instruction=system_instruction_raw
            )
            
            # Note: We are NOT asking for JSON.
            generation_config = genai.types.GenerationConfig(
                 temperature=0.2,
                 max_output_tokens=2048,
            )

            rsp = model.generate_content(
                contents=[user], # Just send the user prompt
                generation_config=generation_config
            )
            return rsp.text
        except Exception as e:
            return f"// LLM error (Gemini): {e}\n"

    # 2. Check for OpenAI Key as a fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            messages = [
                {"role": "system", "content": system}, # System prompt is the PM charter
                {"role": "user", "content": user}
            ]
            
            rsp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2
                # Note: We are NOT asking for JSON
            )
            return rsp.choices[0].message.content or ""
        except Exception as e:
            return f"// LLM error (OpenAI): {e}\n"

    # 3. No key found
    return f"// NO API KEY SET."
# --- END FIX ---


def parse_task_details(task_code: str):
    """Parses the generated Python code to find the task variable and role."""
    task_variable_name = None
    role = None
    
    # Clean the code string of common LLM artifacts
    clean_code = task_code.strip().lstrip("```python").lstrip("```").rstrip("```").strip()
    
    # Find variable name
    var_match = re.search(r"(\w+)\s*=\s*Task\(", clean_code)
    if var_match:
        task_variable_name = var_match.group(1)
        
    # Find role
    role_match = re.search(r"role\s*=\s*[\"\'](\w+)[\"\']", clean_code)
    if role_match:
        role = role_match.group(1)
        
    return task_variable_name, role

def add_task_import(content: str, task_variable_name: str) -> str:
    """Adds the new task variable to the 'from agents.tasks import ...' line."""
    pattern = re.compile(r"(from agents\.tasks import .*)")
    
    def replacer(match):
        import_line = match.group(1)
        if task_variable_name in import_line:
            return import_line 
        return f"{import_line}, {task_variable_name}"

    new_content, count = pattern.subn(replacer, content, 1)
    if count == 0:
        raise Exception("Could not find the task import line 'from agents.tasks import ...'")
    return new_content

def add_task_to_dict(content: str, task_key: str, task_variable_name: str) -> str:
    """Adds the new task key-value pair to the 'TASKS = {...}' dictionary."""
    pattern = re.compile(r"(TASKS = {\n)([^}]+)(\n})")
    
    if f'"{task_key}"' in content:
        print(f"   Task key '{task_key}' already exists. Skipping dictionary add.")
        return content

    new_task_line = f'    "{task_key}": {task_variable_name},\n'
    
    def replacer(match):
        return f"{match.group(1)}{match.group(2)}{new_task_line}{match.group(3)}"

    new_content, count = pattern.subn(replacer, content, 1)
    if count == 0:
        raise Exception("Could not find the 'TASKS = {...}' dictionary.")
    return new_content


def create_new_task(goal: str):
    print(f"🤖 Project Manager Agent activated. Goal: '{goal}'")
    
    # 1. Load PM Charter
    pm_charter_path = ROOT / "agents" / "pm_agent.md"
    if not pm_charter_path.exists():
        print(f"❌ Error: {pm_charter_path} not found.")
        return
    system_prompt = pm_charter_path.read_text()

    # 2. Load existing tasks for context
    tasks_file_path = ROOT / "agents" / "tasks.py"
    tasks_context = tasks_file_path.read_text()

    # 3. Build user prompt
    user_prompt = f"""
Here is the current content of `agents/tasks.py`. Read it to understand the `Task` dataclass and to see examples of existing tasks so you don't duplicate them.

--- START agents/tasks.py ---
{tasks_context}
--- END agents/tasks.py ---

My new goal is: "{goal}"

Please return the *entire* `agents/tasks.py` content, with the new Task object added to the end.
"""

    # 4. Call the local LLM function
    print("🧠 Calling LLM to generate updated file content...")
    raw_llm_output = _llm_complete_raw(system=system_prompt, user=user_prompt).strip()
    
    if raw_llm_output.startswith("//") or not raw_llm_output:
        print(f"❌ {raw_llm_output}")
        return

    # --- START FIX ---

    # 5. Clean the *new file content* from the LLM
    new_file_content = raw_llm_output.lstrip("```python").lstrip("```").rstrip("```").strip()
    
    # 6. Isolate the *new task code* by "subtracting" the old context
    # This is how we find the new task's name for auto-assignment
    new_task_code = new_file_content.replace(tasks_context, "").strip()
    
    if not new_task_code:
        print("❌ Error: LLM did not add any new code. Nothing to do.")
        print("Raw LLM Output:", new_file_content)
        return

    # 7. *Overwrite* the file with the new, complete content
    try:
        with open(tasks_file_path, "w") as f:  # <-- Changed from "a" to "w"
            f.write(new_file_content)
        
        print(f"\n✅ Successfully updated `{tasks_file_path}` with the new task:")
        print("---------------------------------")
        print(new_task_code) # Print just the new part
        print("---------------------------------")

    except Exception as e:
        print(f"❌ Error writing to {tasks_file_path}: {e}")
        return
    # --- END FIX ---

    # 8. AUTOMATED ASSIGNMENT STEP
    print("\n🤖 Now attempting to auto-assign task in `scripts/dev_loop.py`...")
    try:
        # 8a. Parse the *isolated new task code*
        task_variable, role = parse_task_details(new_task_code)
        if not task_variable or not role:
            raise Exception(f"Could not parse new task's variable name or role from: {new_task_code}")
        
        # 8b. Create a unique task key
        task_key = f"{role}:{task_variable.lower().replace('_', '-')}"
        
        # 8c. Read, modify, and write dev_loop.py
        dev_loop_path = ROOT / "scripts" / "dev_loop.py"
        dev_loop_content = dev_loop_path.read_text()
        
        dev_loop_content = add_task_import(dev_loop_content, task_variable)
        dev_loop_content = add_task_to_dict(dev_loop_content, task_key, task_variable)
        
        dev_loop_path.write_text(dev_loop_content)
        
        print(f"✅ Successfully assigned task as '{task_key}' in `{dev_loop_path}`.")
        print(f"\n🚀 You can now run the new task with:")
        print(f"   python3 scripts/dev_loop.py {task_key}")

    except Exception as e:
        print(f"❌ Error auto-assigning task: {e}")
        print("🔔 Please assign the task manually in `scripts/dev_loop.py`.")


def main():
    parser = argparse.ArgumentParser(description="Project Manager Agent: Create & assign new tasks.")
    parser.add_argument("goal", type=str, nargs='+', help="The natural language goal. (e.g., 'write tests for the watches page')")
    args = parser.parse_args()
    create_new_task(" ".join(args.goal))

if __name__ == "__main__":
    main()