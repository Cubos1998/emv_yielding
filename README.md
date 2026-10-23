# EMV yielding

A social-force model of how surrounding traffic makes way for an emergency vehicle (EMV). Drivers perceive the vehicle, react after a delay, and move under a combination of car-following, lane-keeping, point-repulsion and corridor-repulsion forces. Competition between the corridor push and lane resistance gives an idealised depinning threshold.

This repository accompanies **Making Way: A Social Force Model Approach to Emergency Vehicle Traffic Dynamics**, manuscript v5, September 17, 2026. The paper uses `bluelight_params()` (`TUNED_BLUELIGHT`), the two-stage calibration completed on August 6, 2026. The name refers to the Python parameter preset; it is distinct from SUMO's native blue-light device.

[Read the paper](paper/making_way/new_paper_v5.pdf) · [Version provenance](docs/PROVENANCE.md) · [Reproduce the results](docs/REPRODUCIBILITY.md) · [Validation](docs/VALIDATION.md)

## Install and run

Python 3.10 or later is required. From this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python examples/run_scenario.py --scenario overtake --seed 21
python scripts/check.py
```

On Windows, create the environment with `py -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1` in PowerShell.

The example uses the paper preset and writes metrics to `out/example_overtake.json`. It also supports `--scenario jam`, `--scenario highd`, and `--no-yield` for the control condition. No external dataset or traffic simulator is needed for these runs.

```python
from emv.params import bluelight_params
from emv.scenarios import make_overtake
from emv.metrics import evaluate, summary_line

simulation = make_overtake(seed=21, p=bluelight_params())
history = simulation.run(60.0, rec_dt=0.1)
print(summary_line(evaluate(history)))
```

For the interactive parameter lab, run `python experiments/live_lab.py --preset paper`. This requires a graphical desktop and a Matplotlib GUI backend. For the manuscript experiment set:

```bash
python paper/making_way/make_figures.py
python scripts/check_paper_results.py
```

This regenerates the multi-seed simulations and figures under `out/paper/`, using archived calibration and theory records. It does not recalibrate the model. See the reproduction guide for raw-data requirements and the difference between a quick run and the full experiment.

## What is included

| Path | Purpose |
| --- | --- |
| `emv/` | Forces, perception, integration, scenarios, metrics and calibration |
| `emv/sumo/` | Optional SUMO/TraCI coupling |
| `emv/data/reference/` | Historical aggregate records used by the paper |
| `experiments/` | Calibration, validation, sensitivity, theory and demo scripts |
| `examples/` | Small standalone example using the paper preset |
| `tests/` | Original scientific regression checks and package checks |
| `paper/making_way/` | v5 manuscript, required figures and recorded results |
| `docs/` | Provenance, reproduction instructions and technical research notes |

`Params()` and `tuned_params()` retain the earlier default and calibration values for existing research checks. Older experiments such as `run_all.py`, `run_multiseed.py` and the SUMO comparison use those historical settings. Use the manuscript figure script or the example above for the v5 preset.

## Interpretation and limits

The stored full experiment reports mean EMV speed ratios of **0.894 vs 0.824** in the overtake scenario and **0.704 vs 0.286** in the jam, with yielding versus no yielding. The jam yielding runs contain **183 overlapping frame-pairs over five seeds**. This metric counts repeated overlaps, not distinct crashes; the model is not collision-free. The idealised depinning threshold does not guarantee completion of a safe lane change.

Stage 1 fits ordinary traffic to highD measurements. Stage 2 fits four EMV repulsion parameters on that frozen base. Fresh simulation seeds are not held-out real videos, and the fitted model does not reproduce every empirical distribution. Raw highD trajectories, dashcam videos and per-frame annotations are not included. Existing aggregate records allow the manuscript simulations and plots to run without them.

The source snapshot contained no license file. No new license has been assigned here; the project owner still needs to select the terms for a public release. The manuscript and external data retain their own authorship and rights. GitHub publication has not been performed.
