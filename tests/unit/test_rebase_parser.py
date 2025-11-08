from pathlib import Path
from git_pal.rebase.parser import parse_todo_file, write_todo_file

GIT_REBASE_TODO_CONTENT = """\
pick a1b2c3d commit 1
# a comment
reword e4f5a6b commit 2
edit 7c8d9e0 commit 3
squash f1a2b3c commit 4
fixup d4e5f6a commit 5
exec my-script.sh
break
drop b7c8d9e commit 6
label my-label
reset my-label
"""

def test_parse_full_todo(tmp_path: Path):
    todo = tmp_path / "todo"
    todo.write_text(GIT_REBASE_TODO_CONTENT, encoding="utf-8")
    actions = parse_todo_file(todo)
    # Length and spot checks
    assert len(actions) == 11
    assert actions[0].command == "pick" and actions[0].commit_hash == "a1b2c3d"
    assert actions[1].command == "#" and actions[1].message.strip() == "a comment"
    assert any(a.command == "squash" for a in actions)
    assert any(a.command == "exec" and a.message == "my-script.sh" for a in actions)

def test_round_trip(tmp_path: Path):
    """Test that parse -> write -> parse produces identical results."""
    todo = tmp_path / "todo"
    todo.write_text(GIT_REBASE_TODO_CONTENT, encoding="utf-8")

    # First parse
    actions1 = parse_todo_file(todo)

    # Write to new file
    output = tmp_path / "output"
    write_todo_file(output, actions1)

    # Parse again
    actions2 = parse_todo_file(output)

    # Should have same number of actions
    assert len(actions1) == len(actions2)

    # Each action should match
    for a1, a2 in zip(actions1, actions2):
        assert a1.command == a2.command
        assert a1.commit_hash == a2.commit_hash
        assert a1.message == a2.message

def test_merge_command(tmp_path: Path):
    """Test that merge commands are parsed correctly."""
    todo_content = "pick a1b2c3d commit 1\nmerge def4567 Merge feature branch\n"
    todo = tmp_path / "todo"
    todo.write_text(todo_content, encoding="utf-8")

    actions = parse_todo_file(todo)
    assert len(actions) == 2
    assert actions[1].command == "merge"
    assert actions[1].commit_hash == "def4567"
    assert actions[1].message == "Merge feature branch"
