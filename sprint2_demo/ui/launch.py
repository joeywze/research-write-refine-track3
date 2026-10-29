"""Launch the local app; optionally accept a temporary key in this console."""
from getpass import getpass
import argparse
from pathlib import Path
import os
import subprocess
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a port between 1024 and 65535")
    folder = Path(__file__).resolve().parent
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["TRACK3_LOCAL_LIVE"] = "0"
    print("Research Write Refine — http://127.0.0.1:" + str(args.port))
    print("Live mode; the key is not saved in a file." if args.live else "Recorded-run mode; paid calls are disabled.")
    key = (os.environ.get("OPENAI_API_KEY", "").strip() or getpass("OpenAI key (input hidden): ").strip()) if args.live else ""
    if args.live and not key:
        print("No key entered. The live server was not started.")
        return 2
    if key:
        if not key.isascii() or any(c.isspace() for c in key):
            print("The key contains spaces or non-ASCII characters. No server was started.")
            return 2
        env["OPENAI_API_KEY"] = key
        env["TRACK3_LOCAL_LIVE"] = "1"
    else:
        env.pop("OPENAI_API_KEY", None)
    del key
    print("Keep this window open while using the app. Close it only after any live run has finished.")
    try:
        return subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py",
                                "--server.address=127.0.0.1", "--server.port=" + str(args.port)], cwd=folder, env=env)
    finally:
        env.pop("OPENAI_API_KEY", None)


if __name__ == "__main__":
    raise SystemExit(main())
