# Camera-ready figures (ITEC Asia-Pacific 2026)

The camera-ready version of *Making Way: A Social Force Model Approach to Emergency
Vehicle Traffic Dynamics* uses the figures below. All scripts run from the repository
root and write into `paper/making_way/figs/`.

| Paper figure | File | Script |
|---|---|---|
| Fig. 1 (pipeline) | `figs/fig1_pipeline_v4_large.pdf` | `make_v4_large_figures.py` |
| Fig. 2 (force fields, linear scale) | `figs/fig_fields_rev1.pdf` | `make_fig2_rev1.py` |
| Fig. 3 (snapshots) | `figs/fig2_snapshots.pdf` | `make_figures.py` |
| Fig. 4 (bow wave) | `figs/fig3_bowwave_rev2.pdf` | `make_figs45_rev2.py sim`, then `make_figs45_rev2.py plot` |
| Fig. 5 (depinning) | `figs/fig4_depinning_rev2.pdf` | `make_figs45_rev2.py plot` |

```sh
python paper/making_way/make_v4_large_figures.py      # Fig. 1 (and the older log-scale Fig. 2)
python paper/making_way/make_fig2_rev1.py             # Fig. 2
python paper/making_way/make_figs45_rev2.py sim       # 40 overtaking runs (~2 min, resumable cache in ~)
python paper/making_way/make_figs45_rev2.py plot      # Figs. 4 and 5
```

`make_figs45_rev2.py sim` reproduces the published bow-wave statistics exactly
(736 yield onsets, median 85.7 m, 10th/90th percentiles 42.0/126.0 m).
Fig. 5 is re-plotted from the stored record `emv/data/reference/sfm_theory_tests.json`.

The camera-ready figures differ from the earlier `*_v3` / `fig4_depinning.pdf` versions only
in presentation: a linear colour scale and red vehicles in Fig. 2, panel labels (a)/(b) and
an extra axis tick in Fig. 4, and a legend that no longer overlaps the data in Fig. 5.
