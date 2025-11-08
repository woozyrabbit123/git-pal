from typing import List, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Button
from textual.containers import Vertical, Horizontal

from git_pal.rebase.state import RebaseAction
from git_pal.tui.screens.modals import EditActionModal

class RebaseScreen(Screen[List[RebaseAction]]):
    BINDINGS = []

    def __init__(self, initial_actions: List[RebaseAction], features: list[str] | None = None):
        super().__init__()
        self.initial_actions = initial_actions
        self.actions: List[RebaseAction] = [RebaseAction(a.command, a.commit_hash, a.message) for a in initial_actions]
        self.features = set(features or [])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False, name=f"git-pal Rebase Editor [{'PRO' if 'pro' in self.features else 'DEMO'}]")
        yield Vertical(
            DataTable(id="rebase-table", cursor_type="row"),
            Horizontal(
                Button("Save & Exit", variant="success", id="save"),
                Button("Abort", variant="error", id="abort"),
                id="button-bar",
            ),
            id="main-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Action", "SHA", "Message")
        for i, a in enumerate(self.actions):
            if a.command.startswith("#"):
                continue
            table.add_row(a.command, a.commit_hash, a.message, key=str(i))
        table.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            if "pro" in self.features:
                # (future hook) compute smart suggestions here
                pass
            comments = [a for a in self.initial_actions if a.command.startswith("#")]
            final_actions = self.actions + comments
            self.dismiss(final_actions)
        elif event.button.id == "abort":
            self.dismiss(None)

    def on_data_table_cell_selected(self, _event: DataTable.CellSelected) -> None:
        self.action_edit_row()

    @staticmethod
    def _get_row_index(table: DataTable) -> Optional[int]:
        key = table.get_row_key(table.cursor_row)
        return int(key) if key is not None else None

    def action_edit_row(self) -> None:
        table = self.query_one(DataTable)
        idx = self._get_row_index(table)
        if idx is None:
            return
        self.app.push_screen(EditActionModal(action=self.actions[idx]),
                             lambda new_action: self._on_edit_complete(idx, new_action))

    def _on_edit_complete(self, idx: int, new_action: Optional[RebaseAction]) -> None:
        if not new_action:
            return
        self.actions[idx] = new_action
        table = self.query_one(DataTable)
        row_key = str(idx)
        table.update_cell(row_key, column_key="Action", value=new_action.command)
        table.update_cell(row_key, column_key="SHA", value=new_action.commit_hash)
        table.update_cell(row_key, column_key="Message", value=new_action.message)
