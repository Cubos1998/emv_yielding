"""Run the offline scientific and packaging checks with the active Python."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
for script in ("smoke.py", "test_highd.py", "test_terms.py", "test_package.py"):
    print(f"\nRunning {script}", flush=True)
    subprocess.run([sys.executable, str(root / "tests" / script)], cwd=root, check=True)
subprocess.run([sys.executable, str(root / "experiments/live_lab.py"),
                "--self-test", "--preset", "paper"], cwd=root, check=True)
print("\nAll offline checks passed.")
