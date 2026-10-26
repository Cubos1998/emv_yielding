"""Camera-ready Fig. 4 (bow wave) and Fig. 5 (depinning).
Fig. 4: panel labels (a)/(b), tick at 100 m on the onset histogram.
Fig. 5: legend of panel (b) moved so it no longer overlaps data or the identity line.
Outputs go to figs/fig3_bowwave_rev2.* and figs/fig4_depinning_rev2.*.
Usage:  python make_figs45_rev2.py sim    # simulate 40 overtaking runs (resumable), cache in ~/bowwave_rev2_cache.npz
        python make_figs45_rev2.py plot   # draw both figures (needs the cache for Fig. 4)
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import make_figures as M
from make_figures import plt, CAT_LIGHT, INK, MUTED, EV_COL, COL_W, _clean, bow_wave, _bow_extract
from emv.params import bluelight_params
from emv.scenarios import make_overtake
from emv.metrics import evaluate

FIGS = os.path.join(HERE, "figs")
CACHE = os.path.join(os.path.expanduser("~"), "bowwave_rev2_cache.npz")   # scratch, outside the paper folder
SEEDS = list(range(21, 61))

def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIGS, f"{name}.{ext}"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("wrote", name)

def simulate(p, seeds):
    S, D, U, on = [], [], [], []
    if os.path.exists(CACHE):
        z = np.load(CACHE); done = set(z["done"].tolist())
        S, D, U, on = [z["S"]], [z["D"]], [z["U"]], [z["on"]]
    else:
        done = set()
    for s in seeds:
        if s in done: continue
        h = make_overtake(seed=s, p=p, yielding=True).run(60.0, rec_dt=0.1)
        a, b, c = _bow_extract(h, p)
        S.append(a); D.append(b); U.append(c); on.append(np.asarray(evaluate(h)["react_dists"], float))
        done.add(s)
        tmp = CACHE + ".tmp.npz"
        np.savez(tmp, S=np.concatenate(S), D=np.concatenate(D), U=np.concatenate(U),
                 on=np.concatenate(on), done=np.array(sorted(done)))
        os.replace(tmp, CACHE)
        print("seed", s, "done", flush=True)

def fig_bowwave(p):
    z = np.load(CACHE)
    assert sorted(z["done"].tolist()) == SEEDS, "simulation incomplete"
    onsets = z["on"]
    print("n_onsets", onsets.size, "median", np.median(onsets), "p10", np.percentile(onsets, 10), "p90", np.percentile(onsets, 90))
    c, med, q1, q3, um = bow_wave([(z["S"], z["D"], z["U"])], p)
    rho = 22.0
    a_eff = p.a_pin * (rho / p.rho_ref) ** p.k_rho * (1 - p.urgency_pin_relief * 1.0)
    w_need = 0.5 * (2.2 + 1.8) + p.margin_c
    d_star = w_need + p.B_c * np.log(p.A_c / a_eff)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL_W, 1.28), gridspec_kw=dict(width_ratios=[1.75, 1]))
    a1.fill_between(c, q1, q3, color=CAT_LIGHT["orange"], alpha=0.25, lw=0)
    a1.plot(c, med, color=CAT_LIGHT["orange"], lw=1.2)
    a1.axhline(w_need, color=EV_COL, lw=0.7, ls="--")
    a1.text(196, w_need - 0.1, "required clearance", fontsize=6.3, color=EV_COL, ha="right", va="top")
    a1.axhline(d_star, color=INK, lw=0.7, ls=":")
    a1.text(196, d_star + 0.08, r"closed-form $d^*$", fontsize=6.3, color=INK, ha="right", va="bottom")
    a1.set_xlabel("Distance ahead of EMV (m)"); a1.set_ylabel("Lateral offset (m)")
    a1.set_xlim(-40, 200); a1.set_ylim(0, max(d_star, np.nanmax(q3)) + 0.9)
    au = a1.twinx()
    au.plot(c, um, color=CAT_LIGHT["yellow"], lw=0.9)
    au.set_ylim(0, 1.05); au.set_ylabel("Mean urgency", color=CAT_LIGHT["yellow"])
    au.tick_params(axis="y", colors=CAT_LIGHT["yellow"]); au.spines["top"].set_visible(False)
    _clean(a1); a1.spines["right"].set_visible(False)
    a2.hist(onsets, bins=np.arange(0, 241, 20), color=CAT_LIGHT["blue"], alpha=0.85, lw=0)
    a2.set_xticks([0, 100, 200]); a2.set_xlim(0, 240)
    a2.set_xlabel("Yield onset ahead (m)"); a2.set_ylabel("Vehicles")
    a2.axvline(np.median(onsets), color=INK, lw=0.7, ls=":")
    _clean(a2)
    fig.tight_layout(pad=0.2, w_pad=1.4, rect=(0, 0, 0.985, 1))
    for a, lab, dx in ((a1, "a", -0.22), (a2, "b", -0.42)):
        a.text(dx, 1.0, f"({lab})", transform=a.transAxes, fontsize=8, fontweight="bold", va="bottom")
    save(fig, "fig3_bowwave_rev2")

def fig_depinning():
    theory = json.load(open(os.path.join(M.OUT, "sfm_theory_tests.json")))
    rows = [r for r in theory["depin"] if r["scen"] == "overtake" and np.isfinite(r["x_ctrl"])]
    tr, fit = theory["depin_transition"], theory["depin_fit"]
    x = np.array([r["x_ctrl"] for r in rows]); phi = np.array([r["phi"] for r in rows])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL_W, 1.55))
    xx = np.geomspace(0.3, 12, 200)
    sig = 1 / (1 + np.exp(-tr["slope_k"] * (np.log(xx) - np.log(tr["x_mid"]))))
    a1.scatter(x, phi, s=6, color=CAT_LIGHT["violet"], alpha=0.75, lw=0, zorder=3)
    a1.plot(xx, sig, color=INK, lw=0.9, zorder=4)
    a1.axvline(1.0, color=EV_COL, lw=0.7, ls="--")
    a1.set_xscale("log"); a1.set_xlim(0.3, 12); a1.set_ylim(-0.03, 1.03)
    a1.set_xlabel(r"Control ratio $x$"); a1.set_ylabel("Fraction escaped")
    a1.text(tr["x_mid"] * 1.15, 0.42, rf"midpoint {tr['x_mid']:.1f}", fontsize=6.5, color=INK)
    _clean(a1)
    rel = [r for r in rows if np.isfinite(r["d_meas"]) and r["phi_pooled"] > 0.55 and r["x_ctrl"] > 1.3]
    ds = np.array([r["d_star"] for r in rel]); dm = np.array([r["d_meas"] for r in rel])
    sub = ds < 4.2
    a2.scatter(ds[sub], dm[sub], s=9, color=CAT_LIGHT["aqua"], lw=0, zorder=3, label=r"$d^* < 4.2$ m")
    a2.scatter(ds[~sub], dm[~sub], s=9, facecolor="none", edgecolor=CAT_LIGHT["aqua"], lw=0.6, zorder=3,
               label=r"$d^* \geq 4.2$ m")
    lim = [3.0, 8.4]
    a2.plot(lim, lim, color=INK, lw=0.7, ls="--", label="identity")
    a2.axhline(fit["d_meas_saturation"], color=MUTED, lw=0.6, ls=":")
    a2.set_xlim(lim); a2.set_ylim(1.1, 6.2); a2.set_yticks([2, 3, 4, 5, 6])
    a2.set_xlabel(r"Closed-form $d^*$ (m)"); a2.set_ylabel("Measured (m)")
    a2.legend(loc="lower right", frameon=False, fontsize=6, handlelength=1.2, labelspacing=0.25,
              borderaxespad=0.15)
    _clean(a2)
    print("min measured", dm.min(), "points with d*>5.4 & dm<3.4:", int(((ds > 5.4) & (dm < 3.4)).sum()))
    for a, lab in zip((a1, a2), "ab"):
        a.text(-0.32, 1.04, f"({lab})", transform=a.transAxes, fontsize=8, fontweight="bold")
    fig.tight_layout(pad=0.2, w_pad=1.0)
    save(fig, "fig4_depinning_rev2")

if __name__ == "__main__":
    p = bluelight_params()
    if sys.argv[1] == "sim":
        simulate(p, SEEDS)
    else:
        fig_depinning()
        if os.path.exists(CACHE): fig_bowwave(p)
