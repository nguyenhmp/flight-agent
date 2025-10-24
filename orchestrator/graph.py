# Minimal multi-agent orchestrator (LLM-optional).
import os, pathlib, json, time, re # <-- Import 're'
from typing import Callable, Dict, Any

# Fix the ImportError by adding the project root to the system path
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Now imports resolve correctly from the root
from agents.tasks import Task
from agents import tools

# --- START FIX: Add direct LLM imports ---
try:
    import google.generativeai as genai
    from openai import OpenAI
except ImportError:
    print("❌ Error: Could not import 'google.generativeai' or 'openai'.")
    print("Please run 'pip install -r requirements.txt'")
    sys.exit(1)
# --- END FIX ---


def _llm_complete(system: str, user: str) -> str:
    """Uses the configured LLM API (Gemini or OpenAI) to generate the code proposal."""
    
    # 1. Check for Gemini Key and prioritize it
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            client = genai.GenerativeModel 
            model_name = os.getenv("GEMINI_MODEL", "models/gemini-pro") 

            # --- START PROMPT FIX: Ditch JSON, ask for raw code with a separator ---
            text_prompt_instructions = (
                f"\n\nIMPORTANT: You must output *only* the raw, complete code for each file. "
                f"If you modify multiple files, you MUST separate them with a simple text marker on its own line: "
                f"--- FILE: path/to/your/file.tsx ---"
                f"\nDo not use markdown wrappers."
            )
            
            full_prompt = (
                f"You are a professional software engineer. Follow the System Charter and complete the User Task below. "
                f"{text_prompt_instructions}\n\n"
                f"SYSTEM CHARTER:\n{system}\n\nUSER TASK:\n{user}"
            )
            
            system_instruction_raw_code = (
                "You are a pair programming AI. Your output must be only raw code, "
                "separated by '--- FILE: path/to/file.tsx ---' if there are multiple files."
            )
            # --- END PROMPT FIX ---

            model = client(
                model_name=model_name,
                system_instruction=system_instruction_raw_code
            )
            
            # --- START CONFIG FIX: Ask for text/plain ---
            generation_config = genai.types.GenerationConfig(
                 temperature=0.2,
                 response_mime_type="text/plain", # Ask for plain text, not JSON
                 max_output_tokens=8192
            )
            # --- END CONFIG FIX ---

            rsp = model.generate_content(
                contents=[full_prompt],
                generation_config=generation_config
            )
            return rsp.text
        except ImportError as e:
            print(f"\n--- DETAILED IMPORT ERROR ---")
            print(f"PYTHON SYS.PATH: {sys.path}")
            print(f"ERROR: {e}")
            print(f"-------------------------------\n")
            return f"// LLM error (Gemini): Detailed ImportError - {e}"
        except Exception as e:
            return f"// LLM error (Gemini): {e}\n"

    # 2. Check for OpenAI Key as a fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            # --- START PROMPT FIX: Ditch JSON, ask for raw code with a separator ---
            text_prompt_instructions = (
                f"\n\nIMPORTANT: You must output *only* the raw, complete code for each file. "
                f"If you modify multiple files, you MUST separate them with a simple text marker on its own line: "
                f"--- FILE: path/to/your/file.tsx ---"
                f"\nDo not use markdown wrappers."
            )
            # --- END PROMPT FIX ---
            
            messages = [
                {"role": "system", "content": f"{system}{text_prompt_instructions}"},
                {"role": "user", "content": user}
            ]
            
            rsp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2
                # Note: No response_format, we want raw text
            )
            return rsp.choices[0].message.content or ""
        except ImportError:
            return "// ERROR: OPENAI_API_KEY set, but 'openai' package is not installed. Run 'pip install openai'."
        except Exception as e:
            return f"// LLM error (OpenAI): {e}\n"

    # 3. No key found
    return f"// NO API KEY SET."


def run_task(task: Task) -> Dict[str, Any]:
    if task.role == "backend":
        system = (ROOT / "agents" / "backend_agent.md").read_text()
    else:
        system = (ROOT / "agents" / "frontend_agent.md").read_text()

    # 1. Determine which files to read
    files_to_read = []
    if task.files_to_touch: 
        files_to_read = task.files_to_touch
    
    # 2. Read the file contents to build context
    file_contexts = "\n\n--- EXISTING FILE CONTENTS (FOR CONTEXT) ---\n"
    # We must also include the backend schema so the frontend agent knows what fields to use
    backend_schema_paths = ["app/schemas.py", "app/models.py"]
    
    for relpath in backend_schema_paths:
         try:
            content = tools.read_file(relpath)
            file_contexts += f"--- Reference File: {relpath} ---\n{content}\n\n"
         except FileNotFoundError:
             pass 

    for relpath in files_to_read:
        try:
            content = tools.read_file(relpath)
            file_contexts += f"--- File to Modify: {relpath} ---\n{content}\n\n"
        except FileNotFoundError:
            file_contexts += f"--- File to Create: {relpath} (This file is new) ---\n\n"
    
    # 3. Build a prompt based on the task 
    user_prompt = ""

    # --- START PROMPT FIX ---
    # This is the new, strict set of instructions for the agent
    base_instructions = (
        f"Your task is to achieve the goal below. You will be given the content of several files as context. "
        f"You MUST return the *ENTIRE FINAL* content for each file you are asked to modify or create. "
        f"DO NOT just return the changed lines. DO NOT repeat the context I give you. "
        f"If you are creating a new file, return the complete code for that new file. "
        f"If you are modifying an existing file, return the *entire* file, modified as needed."
    )
    # --- END PROMPT FIX ---

    if task.title == "Fix all type errors using float | None":
        user_prompt = (
            f"Title: {task.title}\nGoal: {task.goal}\n\n"
            f"{base_instructions}\n\n"
            f"Your ONLY task is to replace all Python 3.9 type hints (like `float | None` or `str | None`) "
            f"with the Python 3.10+ `Optional` syntax (like `Optional[float]` or `Optional[str]`). "
            f"DO NOT change any other logic. "
            f"\n\nProject tree: {tools.list_repo()}"
            f"\n{file_contexts}"
        )
    else:
        # General-purpose prompt
        user_prompt = (
            f"Title: {task.title}\nGoal: {task.goal}\nAcceptance: {task.acceptance}\n\n"
            f"{base_instructions}\n\n"
            f"The files you are allowed to modify or create are: {files_to_read}. "
            f"You MUST use the fields from the `Reference File` schemas (like `app/schemas.py`) for any API-related code. "
            f"\n\nProject tree: {tools.list_repo()}"
            f"\n{file_contexts}"
        )

    # --- START PARSING FIX: Ditch JSON, use regex splitting ---
    raw_llm_output = _llm_complete(system, user_prompt)
    changes = []
    
    if raw_llm_output.startswith("//"):
         print(f"--- LLM ERROR ---")
         print(raw_llm_output)
         return {"proposal": raw_llm_output, "changes": [], "error": raw_llm_output}
    
    try:
        # Split the output by our '--- FILE: path/to/file ---' separator
        file_blocks = re.split(r'--- FILE: (.*?) ---', raw_llm_output, flags=re.DOTALL)
        
        if len(file_blocks) == 1:
            # No separator found, assume it's a single file
            if not files_to_read:
                 raise ValueError("LLM returned one code block but no `files_to_touch` were specified.")
            
            relpath = files_to_read[0] # Assume it's the first file
            new_content = raw_llm_output.strip().lstrip("```python").lstrip("```").rstrip("```").strip()
            
            if not new_content:
                raise ValueError("LLM returned empty content.")

            print(f"Applying single file change to: {relpath}")
            changes.append(tools.write_file(relpath, new_content))

        else:
            # Separators found, loop through them
            for i in range(1, len(file_blocks), 2):
                relpath = file_blocks[i].strip()
                new_content = file_blocks[i+1].strip().lstrip("```python").lstrip("```").rstrip("```").strip()
                
                if not relpath or not new_content:
                    continue

                if relpath not in files_to_read:
                    print(f"Warning: Skipping file {relpath}, it was not in the task's `files_to_touch` list.")
                    continue
                
                print(f"Applying change to: {relpath}")
                changes.append(tools.write_file(relpath, new_content))

    except Exception as e:
        print(f"--- FAILED TO PARSE OR APPLY CHANGES ---")
        print(f"Error: {e}")
        print("Raw LLM Output:")
        print(raw_llm_output)
        return {"proposal": raw_llm_output, "changes": [], "error": f"ParsingError: {e}"}

    return {"proposal": raw_llm_output, "changes": changes}
    # --- END PARSING FIX ---