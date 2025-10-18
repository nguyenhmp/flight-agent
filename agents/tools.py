import subprocess, os, json, pathlib, shlex
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]

def run_shell(cmd: str, cwd: Optional[str] = None, timeout: int = 120) -> dict:
    """Run a shell command and capture output."""
    proc = subprocess.run(cmd, shell=True, cwd=cwd or ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return {"cmd": cmd, "code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}

def write_file(relpath: str, content: str) -> dict:
    path = ROOT / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return {"path": str(path), "bytes": len(content.encode("utf-8"))}

def read_file(relpath: str) -> str:
    path = ROOT / relpath
    return path.read_text()

def list_repo(relpath: str = ".") -> list[str]:
    path = ROOT / relpath
    return [str(p.relative_to(ROOT)) for p in path.rglob("*") if p.is_file()]
