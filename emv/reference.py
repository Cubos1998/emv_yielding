"""Resolve generated research records, with packaged historical fallbacks."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = Path(__file__).resolve().parent / "data" / "reference"

def record_path(name: str) -> str:
    generated = ROOT / "out" / name
    return str(generated if generated.is_file() else REFERENCE / name)
