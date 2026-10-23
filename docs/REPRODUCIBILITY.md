# Reproducing the research

Run commands from the repository root after `python -m pip install -e .`.

## Standalone checks

```bash
python scripts/check.py
python examples/run_scenario.py --scenario overtake --seed 21
python examples/run_scenario.py --scenario jam --seed 21
```

The check runner executes the original default-preset smoke test, the highD measurement checks on synthetic tracks, the force-budget/two-stage nesting checks, package-data checks, and a headless live-lab recycling/resizing test. The original smoke test's zero-overlap assertion applies to its default preset and selected seeds; it is not a claim about the paper preset.

## Manuscript simulations and figures

```bash
python paper/making_way/make_figures.py
python scripts/check_paper_results.py
```

The full experiment uses the original seed sets: 10 each for overtake and highD-like traffic, five for the jam, with yielding and no-yield controls; the bow-wave analysis pools 40 overtake seeds. Results go to `out/paper/results.json`; plots and generated parameter tables go alongside it. `--quick` uses three seeds and is only a smoke run. Its numbers are not expected to match the manuscript.

The figure generator runs new trajectories but reads historical calibration, validation, depinning and runtime records from `emv/data/reference/`. Consequently, reproducing the figures is not an independent reproduction of calibration or the machine-dependent runtime benchmark. The checker compares the generated JSON with `paper/making_way/reference_results.json`, including seed lists, metrics, overlap counts and calibration summaries. Small floating-point differences are tolerated.

New `out/highd_recordings.json` files override the packaged scenario inputs. Use a fresh checkout, or move those generated records aside, when comparing against the historical paper. The paper generator's other reference inputs remain fixed to the packaged archive.

To compile the preserved manuscript, install a LaTeX distribution containing IEEEtran and its declared packages, then run:

```bash
cd paper/making_way
latexmk -pdf -interaction=nonstopmode -halt-on-error new_paper_v5.tex
```

All required manuscript figures and the parameter table are included. The source and PDF remain the original v5 edition, including its limitations and acknowledgment. Rebuilding figures is optional for compiling it.

## Calibration and data requirements

Packaged records contain aggregate statistics and fitted values, not raw trajectory tracks or video frames. `highd_recordings.json` includes per-recording/carriageway summaries used to set scenario geometry, fleet composition and density. These are necessary to reproduce the highD-like paper scenario; hard-coded fallback geometry gives different results.

To refit using separately obtained highD data:

```bash
python scripts/prepare_reference.py
python experiments/run_highd_extract.py --zip /path/to/highD-dataset-v1.0.zip
python experiments/run_normal_calibration.py --block joint
python experiments/run_normal_validation.py --blocks out/normal_calibration_joint.json
```

The extraction also creates `out/highd_pools.npz`, needed for distributional fitting. That file and the raw dataset are not shipped. `EMV_HIGHD_ZIP` can replace the `--zip` argument. The preparation script copies historical records into `out/` only when absent, for older experiment scripts that read that location directly. It never overwrites a new fit. This example refits the joint block; it is not a claim to recreate every historical search/warm-start sequence.

Stage 2 additionally requires the external dashcam pipeline's per-video directories of `t*.json` annotations:

```bash
python experiments/run_ev_calibration.py --gt-dir /path/to/processed/videos
```

`EMV_GT_DIR` can supply that directory. The original scripts write fitted parameters to JSON; they do not automatically replace constants in `emv/params.py`. Stage 2 uses `TUNED_NORMAL`, so inspect and explicitly promote a new stage-1 fit before claiming to run a newly calibrated two-stage pipeline.

Sensitivity, theory and timing experiments are available as `run_sfm_param_sensitivity.py`, `run_sfm_theory_tests.py` and `run_realtime_bench.py`; each supports `--quick`. Their outputs are generated research artifacts and are ignored by Git.

## Optional SUMO

Install the SUMO application separately and make its binaries discoverable on `PATH` or via `SUMO_HOME`. The historical comparison used SUMO 1.26. Python clients can be installed with `python -m pip install -e '.[sumo]'`; use matching application/client versions for repeatable comparisons. Run `python experiments/play_sumo.py` for the GUI or `python experiments/run_sumo_compare.py` for the older comparison experiment. SUMO is not required by the v5 manuscript experiments.

## Publication scope

The new folder contains no inherited Git history or remote. Generated outputs, environments, local data and credentials are ignored. A public license was not present in the source and has not been chosen on the owner's behalf. Publication and the licensing decision remain with the project owner.
