"""Compatibility launcher; maintained script: src/research/generate_ai_sections.py."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "research/generate_ai_sections.py"), run_name="__main__")
