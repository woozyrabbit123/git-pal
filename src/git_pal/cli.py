import sys
import traceback
from pathlib import Path
from typing import Optional, List

if sys.version_info < (3, 11):
    import tomli as tomllib  # noqa: F401
else:
    import tomllib  # noqa: F401

from git_pal.tui.app import GitPalApp, TUIQuitRequest
from git_pal.rebase.parser import parse_todo_file, write_todo_file
from git_pal.rebase.state import RebaseAction  # placeholder type

def main() -> None:
    """
    Entry point for 'git-pal'. Designed to be called by Git as a GIT_SEQUENCE_EDITOR.
    """
    try:
        if len(sys.argv) < 2:
            print("Error: git-pal is intended to be run by Git as a sequence editor.", file=sys.stderr)
            print('Usage: git config --global sequence.editor "git-pal"', file=sys.stderr)
            sys.exit(1)

        todo_file_path = Path(sys.argv[1])
        if not todo_file_path.is_file():
            print(f"Error: Todo file not found at {todo_file_path}", file=sys.stderr)
            sys.exit(1)

        initial_actions: List[RebaseAction] = parse_todo_file(todo_file_path)

        app = GitPalApp(initial_actions=initial_actions, todo_file_path=todo_file_path)
        final_actions: Optional[List[RebaseAction]] = app.run()

        if final_actions is not None:
            write_todo_file(todo_file_path, final_actions)
            sys.exit(0)

        print("Rebase aborted by user.", file=sys.stderr)
        sys.exit(1)

    except TUIQuitRequest:
        print("Rebase aborted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error running git-pal TUI:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
