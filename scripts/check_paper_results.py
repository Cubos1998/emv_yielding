"""Compare a full manuscript regeneration with the preserved reference JSON."""
import argparse
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[1]


def differences(expected, actual, path="results"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            return [f"{path}: keys differ"]
        return [d for key in expected for d in differences(expected[key], actual[key], f"{path}.{key}")]
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return [f"{path}: list lengths differ"]
        return [d for i, (e, a) in enumerate(zip(expected, actual)) for d in differences(e, a, f"{path}[{i}]")]
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        equal = (math.isnan(expected) and math.isnan(actual)) or math.isclose(expected, actual, rel_tol=1e-7, abs_tol=1e-8)
    else:
        equal = expected == actual
    return [] if equal else [f"{path}: expected {expected!r}, got {actual!r}"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=root / "out/paper/results.json")
    args = parser.parse_args()
    if not args.path.is_file():
        parser.error("Run python paper/making_way/make_figures.py first (without --quick).")
    expected = json.loads((root / "paper/making_way/reference_results.json").read_text())
    actual = json.loads(args.path.read_text())
    errors = differences(expected, actual)
    if errors:
        raise SystemExit("Paper result mismatch:\n" + "\n".join(errors[:30]))
    print("All paper result fields match the preserved reference within tolerance.")
