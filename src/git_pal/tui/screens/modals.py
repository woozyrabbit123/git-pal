from typing import Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Input, Label
from textual.containers import Grid, Vertical, Horizontal

from git_pal.rebase.state import RebaseAction

class ExitConfirmModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    ExitConfirmModal { align: center middle; }
    #dialog { grid-size: 2; grid-gutter: 1 2; width: 60; padding: 0 1; background: $surface; border: thick $background 80%; }
    #question { column-span: 2; content-align: center middle; padding: 1 0; }
    Button { width: 100%; }
    """
    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Abort the rebase? (No changes will be saved)", id="question"),
            Button("Cancel", id="cancel"),
            Button("Abort Rebase", variant="error", id="abort"),
            id="dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "abort")

class LicenseModal(ModalScreen[None]):
    DEFAULT_CSS = """
    LicenseModal { align: center middle; }
    #dialog { width: 80%; max-width: 80; padding: 1 2; background: $error; border: thick $background 80%; }
    #title { content-align: center; width: 100%; padding-bottom: 1; }
    """
    def __init__(self, error_message: str):
        super().__init__()
        self.error_message = error_message
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("License Verification Failed", id="title"),
            Static(self.error_message, id="message"),
            Button("Quit", variant="error", id="quit"),
            id="dialog",
        )
    def on_button_pressed(self, _event: Button.Pressed) -> None:
        self.app.exit(None)

class EditActionModal(ModalScreen[Optional[RebaseAction]]):
    DEFAULT_CSS = """
    EditActionModal { align: center middle; }
    #edit-dialog { width: 80%; max-width: 100; padding: 1 2; background: $surface; border: thick $background 80%; }
    """
    def __init__(self, action: RebaseAction):
        super().__init__()
        self.action = action
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Edit Rebase Action", id="title"),
            Static(f"SHA: {self.action.commit_hash}", id="sha"),
            Static(f"Msg: {self.action.message}", id="msg"),
            Input(self.action.command, id="input-command"),
            Horizontal(Button("Save", variant="success", id="save"),
                       Button("Cancel", id="cancel")),
            id="edit-dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            new_cmd = self.query_one("#input-command", Input).value
            self.action.command = new_cmd
            self.dismiss(self.action)
        else:
            self.dismiss(None)
