import pytest
from textual.widgets import DataTable

from git_pal.tui.app import GitPalApp
from git_pal.rebase.parser import parse_todo_file, write_todo_file
from git_pal import config as config_mod

pytestmark = pytest.mark.asyncio

TEST_TODO_CONTENT = "pick a1b2c3d commit 1\npick e4f5a6b commit 2\n"

@pytest.fixture
def app(tmp_path, valid_license_token):
    todo_path = tmp_path / "git-rebase-todo"
    todo_path.write_text(TEST_TODO_CONTENT, encoding="utf-8")

    # Setup valid license config
    token, pub = valid_license_token
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        f'license_token = "{token}"\n\n[license]\npublic_key = """{pub.decode()}"""\n',
        encoding="utf-8"
    )
    original_get_config_path = config_mod.get_config_path
    config_mod.get_config_path = lambda: cfg_path
    config_mod.load_config.cache_clear()

    actions = parse_todo_file(todo_path)
    app_instance = GitPalApp(initial_actions=actions, todo_file_path=todo_path)

    yield app_instance

    # Cleanup
    config_mod.get_config_path = original_get_config_path
    config_mod.load_config.cache_clear()

async def test_tui_edit_and_save(app: GitPalApp, tmp_path):
    """Test that the TUI launches, displays rebase actions, and can save."""
    async with app.run_test() as pilot:
        await pilot.pause()

        # Wait for the RebaseScreen to be pushed
        from git_pal.tui.screens.rebase import RebaseScreen
        rebase_screen = app.screen
        assert isinstance(rebase_screen, RebaseScreen), f"Expected RebaseScreen, got {type(rebase_screen)}"

        # Get the table from the rebase screen
        table = rebase_screen.query_one("#rebase-table", DataTable)
        assert table.row_count == 2, f"Expected 2 rows, got {table.row_count}"

        # Check initial state
        first_cell = table.get_cell_at((0, 0))
        assert first_cell == "pick", f"Expected 'pick', got '{first_cell}'"

        # Verify initial actions
        assert len(rebase_screen.actions) == 2
        assert rebase_screen.actions[0].command == "pick"
        assert rebase_screen.actions[1].command == "pick"

        # Simulate editing the second action directly in the actions list
        # (In a real scenario, this would happen through the EditActionModal)
        from git_pal.rebase.state import RebaseAction
        rebase_screen.actions[1] = RebaseAction("squash", "e4f5a6b", "commit 2")

        # Click save button
        await pilot.click("#save")
        await pilot.pause()

    # Check the result
    final_actions = app.result
    assert final_actions is not None, "Expected final actions, got None"
    assert len(final_actions) == 2, f"Expected 2 actions, got {len(final_actions)}"
    assert final_actions[0].command == "pick"
    assert final_actions[1].command == "squash"

    # Write and verify file content
    write_todo_file(app.todo_file_path, final_actions)
    content = app.todo_file_path.read_text(encoding="utf-8")
    assert "pick a1b2c3d commit 1" in content
    assert "squash e4f5a6b commit 2" in content
