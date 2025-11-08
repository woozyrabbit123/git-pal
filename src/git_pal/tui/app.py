from pathlib import Path
from typing import List, Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding

from git_pal.rebase.state import RebaseAction
from git_pal.tui.screens.rebase import RebaseScreen
from git_pal.tui.screens.modals import LicenseModal, ExitConfirmModal
from git_pal.licensing import verify_license, LicenseData

class TUIQuitRequest(Exception):
    """Signal a clean TUI quit."""

class GitPalApp(App[Optional[List[RebaseAction]]]):
    CSS = """
    Screen { align: center middle; }
    """
    BINDINGS = [
        Binding("q", "request_quit", "Quit"),
        Binding("s", "save", "Save"),
        Binding("e", "edit", "Edit"),
    ]

    def __init__(self, initial_actions: List[RebaseAction], todo_file_path: Path):
        super().__init__()
        self.initial_actions = initial_actions
        self.todo_file_path = todo_file_path
        self.license_data: Optional[LicenseData] = None
        self.result: Optional[List[RebaseAction]] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.license_data = verify_license()
            self.push_screen(RebaseScreen(self.initial_actions), self._on_rebase_result)
        except Exception as e:
            self.push_screen(LicenseModal(str(e)))

    def _on_rebase_result(self, actions: Optional[List[RebaseAction]]) -> None:
        self.result = actions
        self.exit(self.result)

    def action_request_quit(self) -> None:
        self.push_screen(ExitConfirmModal(), self._on_quit_confirm)

    def _on_quit_confirm(self, confirmed: bool) -> None:
        if confirmed:
            self.exit(None)

    def action_save(self) -> None:
        # Delegated to RebaseScreen; kept for binding completeness.
        pass
