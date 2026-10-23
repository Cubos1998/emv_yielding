"""Seed older experiment input paths without overwriting generated results."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
output = root / "out"
output.mkdir(exist_ok=True)
for source in sorted((root / "emv/data/reference").glob("*.json")):
    target = output / source.name
    if target.exists():
        print(f"Kept existing {target.name}")
    else:
        shutil.copyfile(source, target)
        print(f"Prepared {target.name}")
