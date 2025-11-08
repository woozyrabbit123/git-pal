import subprocess
from pathlib import Path
from functools import lru_cache

def _run_git_command(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e.stderr.strip()}")
    except FileNotFoundError:
        raise RuntimeError("Git executable not found. Ensure 'git' is in PATH.")

@lru_cache(maxsize=1)
def get_repo_root(cwd: Path | None = None) -> Path:
    """
    Returns the root directory of the current Git repository.
    Evaluates cwd at call time instead of import time to avoid stale caching.
    """
    cwd = Path(cwd or Path.cwd())
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise FileNotFoundError(f"Not a git repository at {cwd}") from e

def get_merge_base(branch1: str, branch2: str, repo_path: Path) -> str:
    return _run_git_command(["merge-base", branch1, branch2], cwd=repo_path)
