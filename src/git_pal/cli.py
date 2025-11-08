"""GitPal CLI entry point."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from git_pal.tui.app import GitPalApp, TUIQuitRequest
from git_pal.rebase.parser import parse_todo_file, write_todo_file
from git_pal.rebase.state import RebaseAction

def main(argv: list[str] | None = None) -> int:
    """Entry point for the git-pal CLI."""
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="git-pal",
        description="Interactive TUI for Git rebase conflict resolution."
    )
    parser.add_argument(
        "todo_file",
        type=Path,
        help="Path to the Git rebase todo file provided by Git."
    )
    args = parser.parse_args(argv)

    todo_path = args.todo_file
    if not todo_path.exists():
        print(f"[git-pal] error: todo file not found at {todo_path}", file=sys.stderr)
        return 1

    try:
        actions: list[RebaseAction] = parse_todo_file(todo_path)
        app = GitPalApp(initial_actions=actions, todo_file_path=todo_path)
        final_actions = app.run()

        if final_actions is not None:
            write_todo_file(todo_path, final_actions)
            return 0
        else:
            print("[git-pal] rebase aborted by user.", file=sys.stderr)
            return 1
    except TUIQuitRequest:
        print("[git-pal] user exited TUI.")
        return 1
    except Exception as e:
        print(f"[git-pal] fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
