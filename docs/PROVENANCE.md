# Source and paper provenance

The source is the supplied `physics_behaviour_EMV_final/physics_behaviour_EMV` folder. It has no `.git` directory, tags or commit history. An exact historical Git revision therefore cannot be recovered from this snapshot.

The selected manuscript is `paper/new_paper/new_paper_v5.tex`, dated September 17, 2026 in the project log, titled *Making Way: A Social Force Model Approach to Emergency Vehicle Traffic Dynamics*. Its source and PDF are preserved in `paper/making_way/`. The latest edition was selected from the available manuscripts; the source folder is untouched.

## Which code version?

The original package reports `emv.__version__ = "1.0.0"`. This is a package string, not evidence of a tagged release. More precise evidence is available:

1. The source manifest shipped with `paper/code_based_six_page/` matches all 20 original listed files, including the force model, parameters, integration, perception, metrics and calibration scripts. The non-game entries are preserved in `original_source_manifest.json`.
2. `emv/params.py` identifies the ordinary-traffic calibration as `TUNED_NORMAL` and the August 6, 2026 EMV fit as `TUNED_BLUELIGHT`. The latter inherits all 19 stage-1 values and changes only `A_ev=5.9209`, `B_ev=15.4181`, `A_c=2.3529`, and `B_c=2.8568`.
3. The latest paper's `make_figures.py` imports and calls `bluelight_params()`. Its stored `results.json` explicitly records that preset, overtake/highD-like seeds 21–30, jam seeds 21–25, and bow-wave seeds 21–60.
4. The September 15 project-log entry says those paper simulations used the stage-2 preset and that application code was unchanged. Selected matching run-ledger records are preserved in `paper_runs.json`.
5. September 17 entries describe figure-label, manuscript, funding and acknowledgment edits, rather than a new model calibration.

The defensible identification is therefore **the supplied 1.0.0 source snapshot, with the August 6 two-stage calibrated preset, used for the September 15–17 v5 paper series**. The manifest corroborates the shared code snapshot; it is not a Git commit or a v5-specific source archive.

## Clean-copy changes

The clean package is labeled `1.0.0.post1` solely to distinguish this packaging/cleanup revision. This does not invent an upstream release.

- Excluded the Unreal project, Python bridge, bridge tests, launchers, related documentation and assets. Removed `GAME` and `game_params()` from scenarios and their demo references.
- Preserved the scientific force, perception, lane-change, integration, parameter and metric implementations.
- Replaced the interactive lab's game option with an explicit `paper` preset. Removed the game comparison from the older parameter-statistics script.
- Fixed the live lab's older vehicle-recycling code to initialise newer state fields and preserve optional per-driver arrays when resizing the fleet. This affects the interactive demo only, not manuscript scenario generation.
- Moved selected historical JSON records into package data. Readers prefer newly generated `out/` records and otherwise use the packaged references, preserving measured scenario geometry on a fresh installation.
- Changed the dashcam input default to `EMV_GT_DIR` or `data/dashcam`; explicit `--gt-dir` is still supported.
- Kept the paper source, PDF and required figures unchanged. Figure regeneration now writes to `out/paper/` and reads the archived reference records, so the manuscript assets are not overwritten.
- Added packaging, a standalone example, automated checks, documentation and CI. Removed local session settings, large presentation files, draft papers, raw media and build debris.

`source_manifest.json` maps every copied file to its original relative path and SHA-256. Its `clean_sha256` fields describe the finished copy; `modified` distinguishes copied bytes from intentional edits. Added files are listed in `release_manifest.json`. These records identify this snapshot without relying on filesystem modification times.

Historical technical notes are retained with a notice because they describe several calibration generations. Their old performance claims should not be substituted for the v5 reference results.
