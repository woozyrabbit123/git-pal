# git-pal

A Textual TUI assistant for complex git operations.

`git-pal` intercepts your `git rebase -i` and replaces editor friction with an ergonomic TUI.

## Features

- Interactive DataTable editor for `git-rebase-todo`
- Modal editing of actions
- Offline license verification (RS256 JWT)
- Merge helpers: whitespace-only diff detector, AST-based import merge

## Install

```bash
pip install git-pal  # or pip install dist/git_pal-*.whl
```

## Configuration

git-pal requires a valid license.

Create your config:

```bash
# Linux/macOS
mkdir -p ~/.config/git-pal
# Windows: create %APPDATA%\git-pal
```

Create `~/.config/git-pal/config.toml` (or `%APPDATA%\git-pal\config.toml`):

```toml
license_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

[license]
public_key = """-----BEGIN PUBLIC KEY-----
...your key...
-----END PUBLIC KEY-----"""
```

Then set git-pal as your sequence editor:

```bash
git config --global sequence.editor "git-pal"
```

## Usage

```bash
git rebase -i HEAD~5
```

The TUI will open. Arrow keys to navigate; press `e` or Enter to edit; click Save & Exit to write back.
