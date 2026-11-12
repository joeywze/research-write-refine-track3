"""Save run files and append events as they occur. Use a new directory per run."""

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path


def serialise(value):
    return asdict(value) if is_dataclass(value) else value


class RunStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.sequence = 0

    def write(self, name: str, value) -> None:
        path = self.directory / name
        if path.parent != self.directory or path.exists():
            raise ValueError("Each saved file needs a unique name directly inside the run directory")
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(serialise(value), handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)

    def event(self, kind: str, **details) -> None:
        self.sequence += 1
        record = {"sequence": self.sequence, "time_utc": datetime.now(timezone.utc).isoformat(),
                  "kind": kind, **details}
        with (self.directory / "events.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
