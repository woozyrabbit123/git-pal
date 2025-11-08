"""Textual TUI application - placeholder implementation."""

from typing import List
from git_pal.rebase.state import RebaseAction


class TUIQuitRequest(Exception):
    """Exception raised when user quits the TUI."""
    pass


class GitPalApp:
    """Main TUI application - placeholder implementation."""

    def __init__(self, actions: List[RebaseAction]):
        """Initialize the TUI app."""
        self.actions = actions

    def run(self) -> None:
        """Run the TUI app - placeholder implementation."""
        # Placeholder implementation
        pass
