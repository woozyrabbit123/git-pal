"""Textual TUI application - placeholder implementation."""

from pathlib import Path
from typing import List, Optional
from git_pal.rebase.state import RebaseAction


class TUIQuitRequest(Exception):
    """Exception raised when user quits the TUI."""
    pass


class GitPalApp:
    """Main TUI application - placeholder implementation."""

    def __init__(self, initial_actions: List[RebaseAction], todo_file_path: Path):
        """Initialize the TUI app."""
        self.initial_actions = initial_actions
        self.todo_file_path = todo_file_path

    def run(self) -> Optional[List[RebaseAction]]:
        """Run the TUI app - placeholder implementation."""
        # Placeholder implementation
        return None
