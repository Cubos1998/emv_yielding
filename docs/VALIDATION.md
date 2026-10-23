# Validation of the clean copy

Validated locally on October 23, 2026 with Linux, Python 3.14.4, NumPy 2.5.4, Matplotlib 3.11.2 and Pillow 13.0.0.

| Check | Result |
| --- | --- |
| Editable installation and Python compilation | Passed |
| Original default-preset smoke test | Passed all four scenario runs and assertions |
| Original highD and force-term tests | All 78 reported checks passed |
| Package-data and preset checks | Three tests passed |
| Live-lab paper-preset self-test | Passed simulation, recycling, retuning and fleet resizing |
| Example overtake scenario, seed 21 | Passed; metrics written successfully |
| Experiment command-line parsers | All 16 available help commands passed |
| Wheel build and installation outside the checkout | Passed; all 11 reference JSON files present and highD-like simulation runs |
| Full paper regeneration | Passed; original seed sets, approximately 247 seconds |
| Full result comparison | **Byte-for-byte identical** to the preserved paper results JSON |
| Original source integrity | All 76 copied source files still match their original source hashes |

The regenerated `results.json` SHA-256 is:

```text
bde0f999b2d5585478eaf031e031ebd5033b7e16d065587e0d5d75d01dfc133f
```

The scientific force, parameter, state, road geometry, perception, lane-change, integration, measurement, calibration and force-term modules remain byte-identical to the original. The paper source, PDF and required manuscript figures are also preserved unchanged. File-level changes are recorded in `source_manifest.json`.

The live-lab check initially exposed an existing state-schema mismatch: fresh vehicle rows lacked fields added to `VehState`, and resizing treated optional `None` arrays as ordinary arrays. The demo now builds rows through `VehState`, preserves optional fields and checks dimensions after recycling/resizing. Its headless self-test passes. This code is not used by the manuscript experiments.

The GUI was not visually tested on a desktop. The optional SUMO application, raw-data calibration and LaTeX compilation were not run in this environment. The included PDF is the original manuscript. CI is configured for Python 3.10, 3.12 and 3.14, but only Python 3.14 was exercised locally.

No GitHub repository was created or contacted. The new local Git repository has branch `main`, no commits and no remote. The source folder was not modified.
