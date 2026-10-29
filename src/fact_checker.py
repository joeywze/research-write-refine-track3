"""Compatibility launcher; maintained script: src/fact_checking/fact_checker.py."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "fact_checking/fact_checker.py"), run_name="__main__")
