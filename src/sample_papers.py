"""Compatibility launcher; maintained script: src/research/sample_papers.py."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "research/sample_papers.py"), run_name="__main__")
