from dataclasses import dataclass, field

@dataclass
class RebaseAction:
    command: str
    commit_hash: str = ""
    message: str = ""
    original_line: str = field(init=False, repr=False, default="")

    def __post_init__(self):
        self.original_line = self._to_line()

    def _to_line(self) -> str:
        if self.command in ("pick", "reword", "edit", "squash", "fixup", "drop", "merge"):
            return f"{self.command} {self.commit_hash} {self.message}".rstrip()
        if self.command in ("label", "reset", "update-ref", "exec"):
            return f"{self.command} {self.message}".rstrip()
        if self.command in ("break", "noop"):
            return self.command
        if self.command.startswith("#"):
            return f"{self.command}{self.message}"
        return f"{self.command} {self.commit_hash} {self.message}".strip()

    def __str__(self) -> str:
        return self._to_line()
