"""Run a standalone scenario using the paper's two-stage parameter preset."""
import argparse
import json
from pathlib import Path

import numpy as np

from emv.metrics import evaluate, summary_line
from emv.params import bluelight_params
from emv.scenarios import make_highd_like, make_jam, make_overtake


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["overtake", "jam", "highd"], default="overtake")
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--no-yield", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build, duration = {
        "overtake": (make_overtake, 60.0),
        "jam": (make_jam, 70.0),
        "highd": (make_highd_like, 45.0),
    }[args.scenario]
    simulation = build(seed=args.seed, p=bluelight_params(), yielding=not args.no_yield)
    result = evaluate(simulation.run(duration, rec_dt=0.1))
    output = args.output or Path("out") / f"example_{args.scenario}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    def encode(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(type(value).__name__)
    output.write_text(json.dumps({"preset": "bluelight_params", "seed": args.seed,
                                 "scenario": args.scenario, "yielding": not args.no_yield,
                                 "metrics": result}, default=encode, indent=2) + "\n")
    print(summary_line(result))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
