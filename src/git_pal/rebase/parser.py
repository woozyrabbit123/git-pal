import sys
import re
from pathlib import Path
from typing import List
from git_pal.rebase.state import RebaseAction

COMMIT_LINE_RE = re.compile(
    r"^(?P<command>pick|reword|edit|squash|fixup|drop)\s+(?P<hash>[a-f0-9]+)\s+(?P<message>.*)$"
)
OTHER_CMD_RE = re.compile(r"^(?P<command>exec|label|reset|update-ref)\s+(?P<message>.*)$")
NO_ARG_CMD_RE = re.compile(r"^(?P<command>break|noop)$")
COMMENT_RE = re.compile(r"^(?P<command>#)(?P<message>.*)$")

def parse_todo_file(file_path: Path) -> List[RebaseAction]:
    actions: List[RebaseAction] = []
    with file_path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.rstrip()
            if not line:
                continue
            m = COMMIT_LINE_RE.match(line)
            if m:
                actions.append(
                    RebaseAction(command=m.group("command"), commit_hash=m.group("hash"), message=m.group("message"))
                )
                continue
            m = OTHER_CMD_RE.match(line)
            if m:
                actions.append(RebaseAction(command=m.group("command"), message=m.group("message")))
                continue
            m = NO_ARG_CMD_RE.match(line)
            if m:
                actions.append(RebaseAction(command=m.group("command")))
                continue
            m = COMMENT_RE.match(line)
            if m:
                actions.append(RebaseAction(command="#", message=m.group("message")))
                continue
            print(f"Warning: Unrecognized line {idx}: {line}", file=sys.stderr)
            actions.append(RebaseAction(command=line))
    return actions

def write_todo_file(file_path: Path, actions: List[RebaseAction]) -> None:
    with file_path.open("w", encoding="utf-8") as f:
        for action in actions:
            f.write(str(action) + "\n")
