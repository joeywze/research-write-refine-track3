"""Prompt privately in a local console, then run the authorised USD 10 pilot."""
from getpass import getpass
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys

import run_live


def main():
    print("Stage A -> Stage B: provisional integration test")
    print("Writer:", run_live.WRITER)
    print("Checker and writing review:", run_live.CHECKER)
    print("Maximum estimated API token spend: USD 10 across this workspace's test runs.")
    print("A failed grounding check stops refinement. Team A approval remains pending.")
    print("Five fixed development cases must pass before a fresh writing run starts.")
    print("Your key is passed privately to the local test worker and is not saved in a file.")
    if (run_live.ROOT / "pilot_spend.lock").exists():
        print("A previous test lock is present. Ask for it to be checked before starting another run.")
        return 2
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    temporary = not bool(key)
    if temporary:
        if not sys.stdin.isatty():
            print("Open this launcher in an interactive terminal to enter the key privately.", file=sys.stderr)
            return 2
        key = getpass("OpenAI API key (input hidden): ").strip()
        if not key:
            print("No key entered. No model calls were made.")
            return 2
    if not key.isascii() or any(c.isspace() for c in key):
        print("The key contains spaces or non-ASCII characters. Copy only the secret key, without surrounding quotes.")
        return 2
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = key
    env["PYTHONIOENCODING"] = "utf-8"
    del key
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log = run_live.ROOT / "verification" / ("worker-" + timestamp + ".log")
    log.parent.mkdir(exist_ok=True)
    flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0
    try:
        with log.open("w", encoding="utf-8") as handle:
            process = subprocess.Popen([sys.executable, "-u", str(run_live.ROOT / "run_live.py"),
                                        "--execute", "--allow-provisional", "--calibrate-first"], cwd=run_live.ROOT,
                                       env=env, stdin=subprocess.DEVNULL, stdout=handle,
                                       stderr=subprocess.STDOUT, creationflags=flags,
                                       start_new_session=os.name != "nt")
        record = {
            "pid": process.pid, "started_utc": timestamp, "log": str(log), "key_saved_to_file": False}
        run_live.write_json(run_live.ROOT / "verification/active_worker.json", record)
        print("Test started. Keep this window open until it finishes.", flush=True)
        print("Progress is saved in:", log)
        print("Return to the chat and say 'started' while this window stays open.", flush=True)
        exit_code = process.wait()
        record.update(status="COMPLETED" if exit_code == 0 else "STOPPED", exit_code=exit_code,
                      ended_utc=datetime.now(timezone.utc).isoformat())
        run_live.write_json(run_live.ROOT / "verification/active_worker.json", record)
        print("Test finished." if exit_code == 0 else "Test stopped; the saved log explains the result.", flush=True)
        return exit_code
    finally:
        env.pop("OPENAI_API_KEY", None)


if __name__ == "__main__":
    raise SystemExit(main())
