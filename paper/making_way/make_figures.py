"""Figures, numbers and the parameter table for paper/making_way/new_paper_v5.tex.

Fresh simulations (logged to logs/runs.jsonl) with the stage-2 preset
`bluelight_params()`; depinning panels re-plotted from the stored
out/sfm_theory_tests.json; identification numbers read from
out/normal_validation.json, out/normal_calibration_joint.json and
out/ev_calibration.json. Every number quoted in the paper is written to
results.json by this script.

    python paper/making_way/make_figures.py [--quick]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from emv import params as P
from emv.params import Params, bluelight_params
from emv.scenarios import make_overtake, make_highd_like, make_jam
from emv.metrics import evaluate
from emv.runlog import RunLogger
from emv.state import UNAWARE, NOTICED, YIELDING, HOLD
from emv.viz import LIGHT, CAT_LIGHT

FIG = os.path.join(HERE, "figs")
OUT = os.path.join(ROOT, "emv", "data", "reference")
os.makedirs(FIG, exist_ok=True)

INK, INK2, MUTED, GRID = LIGHT["ink"], LIGHT["ink2"], LIGHT["muted"], LIGHT["grid"]
STATE_COL = {UNAWARE: "#a8a7a1", NOTICED: CAT_LIGHT["yellow"],
             YIELDING: CAT_LIGHT["orange"], HOLD: CAT_LIGHT["aqua"]}
EV_COL = CAT_LIGHT["red"]
COL_W, TXT_W = 3.5, 7.16          # IEEE column / text width, inches

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix",
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "savefig.dpi": 300, "pdf.fonttype": 42,
})


def _save(fig, name):
    paths = []
    for ext in ("pdf", "png"):
        p = os.path.join(FIG, f"{name}.{ext}")
        fig.savefig(p, bbox_inches="tight", pad_inches=0.02)
        paths.append(p)
    plt.close(fig)
    return paths


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------ Fig. 1
def fig_pipeline(abbr="EV", name="fig1_pipeline", corridor_lines=None):
    """Paper-size redraw of zones 1-4 of images/framework_schematic.svg."""
    sub = "emv" if abbr == "EMV" else "ev"
    fig = plt.figure(figsize=(TXT_W, 2.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 36); ax.axis("off")

    def box(x, y, w, h, title, lines, edge=INK2, fill="#fcfcfb", tsize=7.6, lsize=6.6, head=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                    fc=fill, ec=edge, lw=0.7, zorder=2))
        if head:
            ax.add_patch(Rectangle((x, y + h - 0.55), w, 0.55, fc=head, ec="none", zorder=3))
        ax.text(x + 0.9, y + h - 1.0, title, fontsize=tsize, fontweight="bold",
                color=INK, va="top", zorder=4)
        for k, ln in enumerate(lines):
            ax.text(x + 0.9, y + h - 3.2 - k * 1.75, ln, fontsize=lsize, color=INK2,
                    va="top", zorder=4)

    def arrow(x0, y0, x1, y1, col=INK2, lw=0.8):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=5,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))

    def zone(x, y, w, h, label, fill, ha="left"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                    fc=fill, ec="none", zorder=1))
        ax.text(x + 0.8 if ha == "left" else x + w / 2, y + h + 0.4, label, fontsize=7.2,
                fontweight="bold", color=INK2, va="bottom", ha=ha)

    # zone 1: inputs
    zone(0.5, 12.2, 19.5, 21.3, "(1) INPUTS", "#f2f1ec")
    box(1.3, 26.3, 17.9, 6.6, "Parameters", ["presets: defaults, stage 1,", "stage 2 (Table I)"])
    box(1.3, 19.4, 17.9, 6.4, "Scenarios", ["motorway overtake,", "jam, highD-like"])
    box(1.3, 12.8, 17.9, 6.1, "Empirical data", ["highD, dashcam passages"], head=CAT_LIGHT["blue"])

    # zone 2: per-step core
    zone(22, 12.2, 51.5, 21.3, "(2) SIMULATION CORE: one step every 0.05 s", "#f2f1ec")
    box(23, 24.6, 15.3, 8.3, "1  Corridor", [*(corridor_lines or [f"project the {abbr} path", "ahead: arc length s,", "lateral offset"])])
    box(40.2, 24.6, 15.3, 8.3, "2  Perception", ["unaware, noticed,", "yielding, hold;", "urgency u"], head=CAT_LIGHT["yellow"])
    box(57.4, 24.6, 15.3, 8.3, "3  Lane choice", ["commit when the", "incentive exceeds", "the lane barrier"], head=CAT_LIGHT["blue"])
    arrow(38.3, 28.7, 40.2, 28.7); arrow(55.5, 28.7, 57.4, 28.7)
    box(23, 17.6, 49.7, 6.2, "4  Forces (accelerations)",
        [(f"drive + car-car + lane keeping + lane incentive  |  {abbr} point field + corridor field (gated by u)" if abbr == "EV" else "drive, car-car, lane keeping, lane incentive  |  EMV point field, corridor field (gated by u)")],
        head=CAT_LIGHT["red"])
    arrow(65, 24.6, 65, 23.8)
    ax.add_patch(FancyBboxPatch((23, 12.8), 49.7, 4.2, boxstyle="round,pad=0,rounding_size=0.8",
                                fc=INK, ec="none", zorder=2))
    ax.text(24, 14.9, r"5  $a_x = a^{\rm drive} + \min(F^{\rm social}_x,\ a^{\rm IDM})$,  clamp, semi-implicit Euler",
            fontsize=7.2, color="#fcfcfb", va="center", zorder=4)
    arrow(47.8, 17.6, 47.8, 17.0)

    # zone 3: measurement & theory
    zone(76, 12.2, 23.5, 21.3, "(3) MEASUREMENT & THEORY", "#f2f1ec")
    box(76.8, 26.3, 21.9, 6.6, "Trajectories and metrics", ["progress, safety, timing;", "same detector as highD"])
    box(76.8, 19.4, 21.9, 6.4, "Per-term influence", ["force budget, ablations"])
    box(76.8, 12.8, 21.9, 6.1, "Depinning theory", [r"escape if $A_c u > a_{\rm pin}^{\rm eff}$; $d^*$"])
    arrow(72.7, 14.9, 76.8, 29.3)
    arrow(20.0, 29.5, 23, 29.5); arrow(20.0, 21.0, 23, 21.0)

    # zone 4: identification
    zone(0.5, 0.5, 99.0, 9.3, "(4) TWO-STAGE IDENTIFICATION: Latin hypercube + Nelder-Mead", "#eaf6f0", ha="center")
    box(1.3, 1.1, 44, 7.6, f"Stage 1: ordinary traffic, {abbr} absent",
        ["19 parameters (car following 8, lateral 7, lane changing 4)", "fitted to highD, free-flow + dense"], head=CAT_LIGHT["blue"])
    box(54.5, 1.1, 44.2, 7.6, "Stage 2: add the emergency vehicle",
        [(f"stage 1 frozen; only A_{sub}, B_{sub}, A_c, B_c fitted" if abbr == "EV" else r"stage 1 frozen; only $A_{\rm emv}$, $B_{\rm emv}$, $A_c$, $B_c$ fitted"), "to the dashcam behaviour fingerprint"], head=CAT_LIGHT["red"])
    arrow(45.3, 4.9, 54.5, 4.9, col=CAT_LIGHT["aqua"], lw=1.0)
    ax.text(49.9, 5.6, "freeze", fontsize=6.3, color=INK2, ha="center")
    arrow(10, 12.8, 10, 8.7, col=CAT_LIGHT["blue"])
    arrow(87, 12.2, 87, 8.7, col=CAT_LIGHT["aqua"])
    ax.text(88, 10.7, "simulated observables", fontsize=6.3, color=INK2)
    ax.text(11, 10.7, "targets", fontsize=6.3, color=INK2)
    return _save(fig, name)


# ------------------------------------------------------------------ v3: force fields
def fig_fields(p, name="fig_fields_v3"):
    """Refined redraw of Fig. 1(a) and Fig. 3(a) of paper/digests/papers_ITEC/SFM_Digest_ITEC.pdf
    (source: experiments/make_methodology_digest_figs.py): magnitude of the car-car
    repulsion and of the EMV point field, evaluated from the expressions in
    emv.forces (car_car, ev_field) at the stage-2 preset, on one colour scale."""
    from matplotlib.colors import LogNorm
    from emv.viz import CMAP_SEQ
    L_car, W_car = 4.6, 1.9

    def cc_mag(dx, dy):                     # |F^cc| on the car at the origin from a neighbour at (dx, dy)
        gx = np.maximum(np.abs(dx) - L_car, 0.05)
        gy = np.maximum(np.abs(dy) - W_car, 0.05)
        q = np.sqrt((gx / p.Bx_v) ** 2 + (gy / p.By_v) ** 2)
        mag = p.A_v * np.exp(-q) + p.A_near * np.exp(-q / p.q_near)
        d = np.hypot(dx, dy) + 1e-9
        w = p.lam_v + (1 - p.lam_v) * 0.5 * (1 + dx / d)
        return np.minimum(mag * w, p.F_cap_v)

    def emv_mag(dx, dy):                    # |F^EMV| on a car at (dx, dy) from the EMV at the origin
        d = np.maximum(np.hypot(dx, dy), 0.5)
        w = p.lam_ev + (1 - p.lam_ev) * 0.5 * (1 + dx / d)
        return np.minimum(p.A_ev * np.exp((p.r_ev - d) / p.B_ev), p.F_cap_ev) * w

    norm = LogNorm(vmin=0.05, vmax=5.0)
    fig = plt.figure(figsize=(COL_W, 1.32))
    axa = fig.add_axes([0.085, 0.25, 0.37, 0.64])
    axb = fig.add_axes([0.53, 0.25, 0.37, 0.64])
    cax = fig.add_axes([0.925, 0.25, 0.018, 0.64])
    panels = ((axa, cc_mag, (-14, 14, -9, 9), [0.2, 1.0], CAT_LIGHT["blue"], (L_car, W_car),
               "(a) Car–car repulsion", [(-3, -4.3), (-6, 2.9)]),
              (axb, emv_mag, (-20, 52, -23, 23), [0.3, 1.0, 3.0], EV_COL, (5.4, 2.0),
               "(b) EMV point field", [(-14, 8), (24, -14), (9, -2)]))
    for ax, fn, ext, lev, col, (L, W), title, lab_pos in panels:
        X, Y = np.meshgrid(np.linspace(ext[0], ext[1], 460), np.linspace(ext[2], ext[3], 300))
        Z = fn(X, Y)
        im = ax.imshow(Z, extent=ext, origin="lower", aspect="equal", cmap=CMAP_SEQ,
                       interpolation="bilinear", norm=norm, zorder=0)
        cs = ax.contour(X, Y, Z, levels=lev, colors=[INK2], linewidths=0.5, zorder=2)
        ax.clabel(cs, fmt="%.2g", fontsize=5.5, inline_spacing=1.2, manual=lab_pos)
        ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc=col, ec=INK, lw=0.4, zorder=5))
        span = ext[1] - ext[0]
        ax.annotate("", xy=(ext[0] + 0.30 * span, ext[3] * 0.72), xytext=(ext[0] + 0.06 * span, ext[3] * 0.72),
                    arrowprops=dict(arrowstyle="-|>", color="white", lw=0.8, mutation_scale=6), zorder=6)
        ax.text(ext[0] + 0.32 * span, ext[3] * 0.72, "driving direction", color="white", fontsize=5.8,
                va="center", zorder=6)
        ax.set_title(title, loc="left", fontsize=7.2, pad=2)
        ax.tick_params(labelsize=6, length=2, pad=1)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
    axa.set_xlabel("Longitudinal offset (m)", fontsize=6.6, labelpad=1)
    axb.set_xlabel("Longitudinal offset (m)", fontsize=6.6, labelpad=1)
    axa.set_ylabel("Lateral offset (m)", fontsize=6.6, labelpad=1)
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(labelsize=5.8, length=1.5, pad=1)
    cb.set_label(r"Acceleration (m/s$^2$)", fontsize=6.2, labelpad=1)
    cb.outline.set_linewidth(0.4)
    return _save(fig, name)


# ------------------------------------------------------------------ Fig. 2
def fig_snapshots(h, frames, p, window=(-50.0, 230.0)):
    ev = h.ev
    road = h.road
    fig, axes = plt.subplots(len(frames), 1, figsize=(TXT_W, 0.6 * len(frames) + 0.32), sharex=True)
    lanes_y = [road.lane_center(k) for k in range(road.n_lanes)]
    w = road.lane_width
    y_lo, y_hi = -road.shoulder_right, road.n_lanes * w + road.shoulder_left
    for ax, k in zip(axes, frames):
        xe = h.x[k, ev]
        ax.add_patch(Rectangle((window[0], 0), window[1] - window[0], road.n_lanes * w,
                               fc="#ecebe6", ec="none", zorder=0))
        for j in range(1, road.n_lanes):
            ax.plot(window, [j * w] * 2, color="white", lw=0.8, ls=(0, (6, 5)), zorder=1)
        for yy in (0, road.n_lanes * w):
            ax.plot(window, [yy] * 2, color=MUTED, lw=0.8, zorder=1)
        v_pred = max(h.vx[k, ev], p.v_app_floor * h.v0[ev])
        L = float(np.clip(v_pred * p.T_pred, p.L_pred_min, p.L_pred_max))
        wn = 0.5 * (h.W[ev] + 1.8) + p.margin_c
        ax.add_patch(Rectangle((0, h.y_corr - wn), L, 2 * wn, fc=EV_COL, alpha=0.10, ec="none", zorder=1))
        ax.plot([0, L], [h.y_corr] * 2, color=EV_COL, lw=0.6, ls=(0, (3, 3)), zorder=1)
        ax.plot([p.R_front] * 2, [y_lo, y_hi], color=INK2, lw=0.6, ls=":", zorder=1)
        rel = h.x[k] - xe
        vis = (rel > window[0] - 10) & (rel < window[1] + 10)
        for i in np.flatnonzero(vis):
            col = EV_COL if i == ev else STATE_COL[int(h.aware[k, i])]
            ax.add_patch(Rectangle((rel[i] - h.L[i] / 2, h.y[k, i] - h.W[i] / 2), h.L[i], h.W[i],
                                   fc=col, ec=INK if i == ev else "none", lw=0.5, zorder=3))
            if i != ev and h.aware[k, i] == YIELDING and abs(h.vy[k, i]) > 0.15:
                ax.annotate("", xy=(rel[i], h.y[k, i] + 1.6 * np.sign(h.vy[k, i])),
                            xytext=(rel[i], h.y[k, i]), zorder=4,
                            arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.5, mutation_scale=5))
        ax.set_xlim(*window); ax.set_ylim(y_lo - 2.8, y_hi + 0.3)
        ax.set_yticks([]); ax.set_aspect("auto")
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.text(1.005, 0.5, f"t = {h.t[k]:.0f} s", transform=ax.transAxes, fontsize=7, va="center", color=INK)
    axes[0].text(p.R_front - 2, y_lo - 1.2, r"detection range $R_{\rm front}$", fontsize=6.5, color=INK2, va="center", ha="right")
    axes[-1].set_xlabel("Longitudinal distance ahead of the emergency vehicle (m)")
    handles = [Rectangle((0, 0), 1, 1, fc=c) for c in (EV_COL, STATE_COL[UNAWARE], STATE_COL[NOTICED],
                                                      STATE_COL[YIELDING], STATE_COL[HOLD])]
    handles.append(Rectangle((0, 0), 1, 1, fc=EV_COL, alpha=0.15))
    fig.legend(handles, ["emergency vehicle", "unaware", "noticed", "yielding", "hold", "predicted corridor"],
               loc="upper center", ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.03), handlelength=1.2)
    fig.subplots_adjust(hspace=0.12)
    return _save(fig, "fig2_snapshots")


# ------------------------------------------------------------------ Fig. 3
def bow_wave(hs, p, s_bins=np.arange(-40, 241, 10.0)):
    """|lateral offset from the corridor line| against distance ahead of the EV
    for vehicles that started inside the required clearance; urgency alongside."""
    S, D, U = [], [], []
    for h in hs:
        if isinstance(h, tuple):
            S.append(h[0]); D.append(h[1]); U.append(h[2]); continue
        ev = h.ev
        wn = 0.5 * (h.W[ev] + h.W) + p.margin_c
        need = np.abs(h.y[0] - h.y_corr) < wn
        need[ev] = False
        idx = np.flatnonzero(need)
        s = h.x[:, idx] - h.x[:, [ev]]
        S.append(s.ravel()); D.append(np.abs(h.y[:, idx] - h.y_corr).ravel()); U.append(h.u[:, idx].ravel())
    S, D, U = map(np.concatenate, (S, D, U))
    c = 0.5 * (s_bins[1:] + s_bins[:-1])
    med, q1, q3, um = [], [], [], []
    for a, b in zip(s_bins[:-1], s_bins[1:]):
        m = (S >= a) & (S < b)
        if m.sum() < 20:
            med.append(np.nan); q1.append(np.nan); q3.append(np.nan); um.append(np.nan); continue
        med.append(np.median(D[m])); q1.append(np.percentile(D[m], 25)); q3.append(np.percentile(D[m], 75))
        um.append(np.mean(U[m]))
    return c, np.array(med), np.array(q1), np.array(q3), np.array(um)


def _bow_extract(h, p):
    """The (s, |d|, u) samples bow_wave() needs, without keeping the history."""
    ev = h.ev
    wn = 0.5 * (h.W[ev] + h.W) + p.margin_c
    need = np.abs(h.y[0] - h.y_corr) < wn
    need[ev] = False
    idx = np.flatnonzero(need)
    return ((h.x[:, idx] - h.x[:, [ev]]).ravel(), np.abs(h.y[:, idx] - h.y_corr).ravel(), h.u[:, idx].ravel())


def fig_bowwave(bw, onsets, d_star, w_need, lane_w, abbr="EV", name="fig3_bowwave"):
    c, med, q1, q3, um = bw
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL_W, 1.55 if abbr == "EV" else 1.40), gridspec_kw=dict(width_ratios=[1.75, 1]))
    a1.fill_between(c, q1, q3, color=CAT_LIGHT["orange"], alpha=0.25, lw=0, label="interquartile range")
    a1.plot(c, med, color=CAT_LIGHT["orange"], lw=1.2, label="median offset")
    a1.axhline(w_need, color=EV_COL, lw=0.7, ls="--")
    a1.text(196, w_need - 0.1, "required clearance", fontsize=6.3, color=EV_COL, ha="right", va="top")
    a1.axhline(d_star, color=INK, lw=0.7, ls=":")
    a1.text(196, d_star + 0.08, r"closed-form $d^*$", fontsize=6.3, color=INK, ha="right", va="bottom")
    a1.set_xlabel(f"Distance ahead of {abbr} (m)"); a1.set_ylabel("Lateral offset (m)")
    a1.set_xlim(-40, 200); a1.set_ylim(0, max(d_star, np.nanmax(q3)) + 0.9)
    au = a1.twinx()
    au.plot(c, um, color=CAT_LIGHT["yellow"], lw=0.9)
    au.set_ylim(0, 1.05); au.set_ylabel("Mean urgency", color=CAT_LIGHT["yellow"])
    au.tick_params(axis="y", colors=CAT_LIGHT["yellow"])
    for s in ("top",):
        au.spines[s].set_visible(False)
    _clean(a1); a1.spines["right"].set_visible(False)
    a2.hist(onsets, bins=np.arange(0, 241, 20), color=CAT_LIGHT["blue"], alpha=0.85, lw=0)
    a2.set_xlabel("Yield onset ahead (m)"); a2.set_ylabel("Vehicles")
    a2.axvline(np.median(onsets), color=INK, lw=0.7, ls=":")
    _clean(a2)
    fig.tight_layout(pad=0.2, w_pad=1.4)
    return _save(fig, name)


# ------------------------------------------------------------------ Fig. 4
def fig_depinning(theory, p):
    rows = [r for r in theory["depin"] if r["scen"] == "overtake" and np.isfinite(r["x_ctrl"])]
    tr, fit = theory["depin_transition"], theory["depin_fit"]
    x = np.array([r["x_ctrl"] for r in rows]); phi = np.array([r["phi"] for r in rows])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL_W, 1.55))

    # (b) escaping fraction against the control ratio
    xx = np.geomspace(0.3, 12, 200)
    sig = 1 / (1 + np.exp(-tr["slope_k"] * (np.log(xx) - np.log(tr["x_mid"]))))
    a1.scatter(x, phi, s=6, color=CAT_LIGHT["violet"], alpha=0.75, lw=0, zorder=3)
    a1.plot(xx, sig, color=INK, lw=0.9, zorder=4)
    a1.axvline(1.0, color=EV_COL, lw=0.7, ls="--")
    a1.set_xscale("log"); a1.set_xlim(0.3, 12); a1.set_ylim(-0.03, 1.03)
    a1.set_xlabel(r"Control ratio $x$")
    a1.set_ylabel("Fraction escaped")
    a1.text(tr["x_mid"] * 1.15, 0.42, rf"midpoint {tr['x_mid']:.1f}", fontsize=6.5, color=INK)
    _clean(a1)

    # (c) measured half-width against the closed form
    rel = [r for r in rows if np.isfinite(r["d_meas"]) and r["phi_pooled"] > 0.55 and r["x_ctrl"] > 1.3]
    ds = np.array([r["d_star"] for r in rel]); dm = np.array([r["d_meas"] for r in rel])
    sub = ds < 4.2
    a2.scatter(ds[sub], dm[sub], s=9, color=CAT_LIGHT["aqua"], lw=0, zorder=3, label=r"$d^* < 4.2$ m")
    a2.scatter(ds[~sub], dm[~sub], s=9, facecolor="none", edgecolor=CAT_LIGHT["aqua"], lw=0.6, zorder=3,
               label=r"$d^* \geq 4.2$ m")
    lim = [3.0, 8.4]
    a2.plot(lim, lim, color=INK, lw=0.7, ls="--", label="identity")
    a2.axhline(fit["d_meas_saturation"], color=MUTED, lw=0.6, ls=":")
    a2.set_xlim(lim); a2.set_ylim(3.0, 6.2)
    a2.set_xlabel(r"Closed-form $d^*$ (m)"); a2.set_ylabel("Measured (m)")
    a2.legend(loc="upper left", frameon=False, fontsize=6, handlelength=1.2, borderaxespad=0.1)
    _clean(a2)
    for a, lab in zip((a1, a2), "ab"):
        a.text(-0.32, 1.04, f"({lab})", transform=a.transAxes, fontsize=8, fontweight="bold")
    fig.tight_layout(pad=0.2, w_pad=1.0)
    return _save(fig, "fig4_depinning"), dict(n_points=int(len(rows)), n_reliable=int(len(rel)),
                                               n_sub=int(sub.sum()), x_mid=tr["x_mid"], slope_k=tr["slope_k"],
                                               phi_below_1=tr["phi_below_1"],
                                               rmse_sub=fit["rmse_vs_identity_sub"],
                                               saturation=fit["d_meas_saturation"],
                                               spearman=fit["spearman_rho"])


# ------------------------------------------------------------------ Table I
TABLE_ROWS = [
    # key, symbol, meaning, unit, block
    ("tau", r"$\tau$", "speed relaxation time", "s", "lon"),
    ("T_hw_lo", r"$T_{\rm lo}$", "headway draw, lower bound", "s", "lon"),
    ("T_hw_hi", r"$T_{\rm hi}$", "headway draw, upper bound", "s", "lon"),
    ("s0", r"$s_0$", "standstill gap", "m", "lon"),
    ("A_v", r"$A_v$", "car--car repulsion strength", r"m/s$^2$", "lon"),
    ("Bx_v", r"$B_x$", "car--car longitudinal range", "m", "lon"),
    ("a_max", r"$a_{\max}$", "comfortable acceleration", r"m/s$^2$", "lon"),
    ("b_comf", r"$b$", "comfortable deceleration", r"m/s$^2$", "lon"),
    ("a_pin", r"$a_{\rm pin}$", "lane-keeping barrier", r"m/s$^2$", "lat"),
    ("zeta_lat", r"$\zeta$", "lateral damping ratio", "--", "lat"),
    ("v_lat_max", r"$v_y^{\max}$", "lateral speed limit", "m/s", "lat"),
    ("a_lat_max", r"$a_y^{\max}$", "lateral acceleration limit", r"m/s$^2$", "lat"),
    ("sigma_off", r"$\sigma_{\rm off}$", "preferred in-lane offset s.d.", "m", "lat"),
    ("het_lat", r"$h_{\rm lat}$", "driver-to-driver dispersion", "--", "lat"),
    ("k_rho", r"$k_\rho$", "density exponent of barrier", "--", "lat"),
    ("A_pass", r"$A_{\rm pass}$", "overtaking incentive", r"m/s$^2$", "lc"),
    ("A_keep_right", r"$A_{\rm keep}$", "keep-right pressure", r"m/s$^2$", "lc"),
    ("T_frust", r"$T_{\rm frust}$", "frustration headway", "s", "lc"),
    ("s_veto", r"$s_{\rm veto}$", "gap-check window", "m", "lc"),
    ("A_ev", r"$A_{\rm ev}$", "EV point-field strength", r"m/s$^2$", "ev"),
    ("B_ev", r"$B_{\rm ev}$", "EV point-field range", "m", "ev"),
    ("A_c", r"$A_c$", "corridor-field strength", r"m/s$^2$", "ev"),
    ("B_c", r"$B_c$", "corridor-field decay", "m", "ev"),
    ("T_react", r"$T_{\rm react}$", "anticipation time", "s", "ev"),
    ("gamma_c", r"$\gamma_c$", "merge-brake gain", r"s$^{-1}$", "ev"),
]
PRESETS = [
    ("default", "Defaults", {}),
    ("tuned", "Behavioural fit", P.TUNED),
    ("highd", "highD lateral fit", P.TUNED_HIGHD),
    ("normal", "Stage 1", P.TUNED_NORMAL),
    ("bluelight", "Stage 2", P.TUNED_BLUELIGHT),
]


def _fmt(v):
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 100:
        return f"{v:.0f}"
    if a >= 10:
        return f"{v:.1f}"
    return f"{v:.2f}"


def param_table():
    base = Params()
    eff = {k: Params().copy(**d) for k, _, d in PRESETS}
    fitted = {
        "default": set(),
        "tuned": set(P.TUNED),
        "highd": set(P.TUNED_HIGHD) - set(P.TUNED),
        "normal": set(P.TUNED_NORMAL),
        "bluelight": set(P.TUNED_BLUELIGHT) - set(P.TUNED_NORMAL),
    }
    lines, record = [], {}
    heads = {"lon": "Car following (stage 1)", "lat": "Lateral block (stage 1)",
             "lc": "Discretionary lane changing (stage 1)", "ev": "Emergency-vehicle response (stage 2)"}
    cur = None
    for key, sym, meaning, unit, blk in TABLE_ROWS:
        if blk != cur:
            lines.append(r"\multicolumn{8}{l}{\emph{" + heads[blk] + r"}}\\")
            cur = blk
        cells = []
        record[key] = {}
        for pk, _, _ in PRESETS:
            v = float(getattr(eff[pk], key))
            record[key][pk] = v
            s = _fmt(v)
            if key in fitted[pk]:
                s = r"\textbf{" + s + "}"
            cells.append(s)
        lines.append(f"{sym} & {meaning} & {unit} & " + " & ".join(cells) + r"\\")
    with open(os.path.join(HERE, "param_table.tex"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    # compact variant for new_paper_v3 (column width): defaults, stage 1, stage 2
    short = {"lon": "Car following (stage 1)", "lat": "Lateral block (stage 1)",
             "lc": "Lane changing (stage 1)", "ev": "EMV response (stage 2)"}
    lines3, cur = [], None
    for key, sym, meaning, unit, blk in TABLE_ROWS:
        if blk != cur:
            lines3.append(r"\multicolumn{6}{l}{\emph{" + short[blk] + r"}}\\")
            cur = blk
        cells = []
        for pk in ("default", "normal", "bluelight"):
            s = _fmt(record[key][pk])
            cells.append(r"\textbf{" + s + "}" if key in fitted[pk] else s)
        sym3 = sym.replace(r"{\rm ev}", r"{\rm emv}")
        lines3.append(f"{sym3} & {meaning.replace('EV ', 'EMV ')} & {unit} & " + " & ".join(cells) + r"\\")
    with open(os.path.join(HERE, "param_table_v3.tex"), "w") as fh:
        fh.write("\n".join(lines3) + "\n")
    return record


# ------------------------------------------------------------------ runs
def summarise(ms):
    keys = ["ev_speed_ratio", "clearance_mean", "min_ttc", "collisions", "react_dist_mean", "n_yielded"]
    out = {}
    for k in keys:
        a = np.array([m[k] for m in ms], dtype=float)
        a = a[np.isfinite(a)]
        out[k] = dict(mean=float(a.mean()) if a.size else float("nan"),
                      sd=float(a.std(ddof=1)) if a.size > 1 else 0.0, n=int(a.size))
    out["collisions_total"] = int(sum(m["collisions"] for m in ms))
    return out


def main():
    global HERE, FIG
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--output-dir", default=os.path.join(ROOT, "out", "paper"),
                    help="Destination for regenerated figures, tables and results")
    a = ap.parse_args()
    HERE = os.path.abspath(a.output_dir)
    FIG = os.path.join(HERE, "figs")
    os.makedirs(FIG, exist_ok=True)
    seeds = [21, 22, 23] if a.quick else list(range(21, 31))
    jam_seeds = seeds[:3] if a.quick else list(range(21, 26))
    p = bluelight_params()
    res = dict(preset="bluelight_params", seeds=seeds, jam_seeds=jam_seeds)
    outputs = []

    with RunLogger("paper_figs", note="new_paper (+v3): pipeline figures, force-field maps, multi-seed yield/no-yield runs, 40-seed bow wave (bluelight_params)",
                   params=dict(n_seeds=len(seeds), quick=a.quick)) as log:
        outputs += fig_pipeline()
        outputs += fig_pipeline(abbr="EMV", name="fig1_pipeline_v3")
        outputs += fig_fields(p)
        outputs += fig_pipeline(abbr="EMV", name="fig1_pipeline_v4",
                                corridor_lines=["project the EMV path", "ahead; sideways", "distance d from it"])

        # scenario runs: yielding vs no yielding
        scen = {
            "overtake": (lambda s, y: make_overtake(seed=s, p=p, yielding=y), 60.0, seeds),
            "highd_like": (lambda s, y: make_highd_like(seed=s, p=p, yielding=y), 45.0, seeds),
            "jam": (lambda s, y: make_jam(seed=s, p=p, yielding=y), 70.0, jam_seeds),
        }
        hist_keep = {}
        for name, (mk, T, ss) in scen.items():
            for y in (True, False):
                ms = []
                for s in ss:
                    h = mk(s, y).run(T, rec_dt=0.1)
                    ms.append(evaluate(h))
                    if name == "overtake" and y:
                        hist_keep[s] = h
                res[f"{name}_{'yield' if y else 'noyield'}"] = summarise(ms)
                if name == "overtake" and y:
                    res["overtake_onsets"] = np.concatenate([m["react_dists"] for m in ms]).tolist()
                print(name, y, {k: round(v["mean"], 3) for k, v in res[f"{name}_{'yield' if y else 'noyield'}"].items()
                                if isinstance(v, dict)}, "coll", res[f"{name}_{'yield' if y else 'noyield'}"]["collisions_total"])

        # Fig. 2 from the first overtake seed
        h0 = hist_keep[seeds[0]]
        frames = [int(round(t / 0.1)) for t in (0.0, 15.0, 30.0)]
        outputs += fig_snapshots(h0, frames, p)
        k2 = frames[1]
        res["snapshot"] = dict(seed=seeds[0], times=[float(h0.t[k]) for k in frames],
                               counts={str(h0.t[k]): np.bincount(h0.aware[k, np.arange(h0.x.shape[1]) != h0.ev],
                                                                 minlength=4).tolist() for k in frames})

        # Fig. 3 bow wave (pooled over seeds)
        bw = bow_wave(list(hist_keep.values()), p)
        rho = 1000.0 / 1000.0 * 22.0                       # make_overtake density, veh/km/lane
        a_eff = p.a_pin * (rho / p.rho_ref) ** p.k_rho * (1 - p.urgency_pin_relief * 1.0)
        w_need = 0.5 * (2.2 + 1.8) + p.margin_c
        d_star = w_need + p.B_c * np.log(p.A_c / a_eff) if p.A_c > a_eff else float("nan")
        onsets = np.array(res["overtake_onsets"])
        outputs += fig_bowwave(bw, onsets, d_star, w_need, 3.5)
        c, med, q1, q3, um = bw
        near = (c > 0) & (c < 40)
        res["bowwave"] = dict(a_pin_eff_u1=float(a_eff), w_need=float(w_need), d_star=float(d_star),
                              control_ratio_u1=float(p.A_c / a_eff),
                              median_offset_0_40=float(np.nanmedian(med[near])),
                              onset_median=float(np.median(onsets)), onset_p10=float(np.percentile(onsets, 10)),
                              onset_p90=float(np.percentile(onsets, 90)), n_onsets=int(onsets.size),
                              urgency_at_150=float(um[np.argmin(np.abs(c - 145))]),
                              urgency_at_50=float(um[np.argmin(np.abs(c - 45))]))

        # Fig. 3 for new_paper_v3: same bow wave pooled over many more seeds.
        # Extracted per run so 40 full histories never sit in memory at once.
        bow_seeds = seeds if a.quick else list(range(21, 61))
        S_parts, onsets3 = [], []
        for s in bow_seeds:
            h = hist_keep[s] if s in hist_keep else make_overtake(seed=s, p=p, yielding=True).run(60.0, rec_dt=0.1)
            S_parts.append(h if s in hist_keep else _bow_extract(h, p))
            onsets3.extend(evaluate(h)["react_dists"].tolist() if s not in hist_keep else [])
        onsets3 = np.array(list(res["overtake_onsets"]) + onsets3)
        bw3 = bow_wave(S_parts, p)
        outputs += fig_bowwave(bw3, onsets3, d_star, w_need, 3.5, abbr="EMV", name="fig3_bowwave_v3")
        c3, med3, q13, q33, um3 = bw3
        res["bowwave_v3"] = dict(n_seeds=len(bow_seeds), seeds=[bow_seeds[0], bow_seeds[-1]],
                                 onset_median=float(np.median(onsets3)),
                                 onset_p10=float(np.percentile(onsets3, 10)),
                                 onset_p90=float(np.percentile(onsets3, 90)), n_onsets=int(onsets3.size),
                                 urgency_at_145=float(um3[np.argmin(np.abs(c3 - 145))]),
                                 urgency_at_45=float(um3[np.argmin(np.abs(c3 - 45))]),
                                 median_offset_behind=float(np.nanmedian(med3[c3 < 0])),
                                 first_zero_urgency_bin=float(c3[np.flatnonzero((um3 == 0) & (c3 > 0))[0]])
                                 if np.any((um3 == 0) & (c3 > 0)) else float("nan"))

        # Fig. 4 depinning (stored record)
        theory = json.load(open(os.path.join(OUT, "sfm_theory_tests.json")))
        paths, dep = fig_depinning(theory, p)
        outputs += paths
        res["depinning"] = dep

        # identification numbers (stored records)
        nv = json.load(open(os.path.join(OUT, "normal_validation.json")))
        nj = json.load(open(os.path.join(OUT, "normal_calibration_joint.json")))
        ec = json.load(open(os.path.join(OUT, "ev_calibration.json")))
        rt = json.load(open(os.path.join(OUT, "realtime_bench.json")))
        res["stage1"] = dict(loss_fit=nj["loss"], loss_prev_single_stage=nj["baselines"]["highd_2026_07_29"]["loss"],
                             loss_default=nj["baselines"]["default"]["loss"], n_evals=nj["n_evals"],
                             blocks={b: {k: (v.get("moment") if isinstance(v, dict) else v) for k, v in d.items()}
                                     for b, d in nv["blocks"].items()},
                             bars={r: v["mean"] for r, v in nv["bars"].items()})
        res["stage2"] = dict(loss_fit=ec["loss"], loss_val=ec["validation"]["loss"],
                             loss_published_block=ec["baselines"]["tuned_ev"]["loss"],
                             loss_defaults=ec["baselines"]["defaults"]["loss"], bar=ec["gt"]["acceptance_bar"],
                             n_evals=ec["n_evals"], gt_frames=ec["gt"]["n_frames"],
                             gt_obs=ec["gt"]["rules"]["n_obs"], n_videos=len(ec["gt"]["videos"]),
                             val_measures=ec["validation"]["measures"])
        row113 = [r for r in rt["rows"] if r["n_veh"] == 113][0]
        res["realtime"] = dict(ms_113=row113["ms_med"], share_60hz=row113["frame_share_60"],
                               n_veh_60hz=rt["n_veh_one_frame_60hz"])
        res["param_table"] = param_table()

        with open(os.path.join(HERE, "results.json"), "w") as fh:
            json.dump(res, fh, indent=1)
        outputs += [os.path.join(HERE, "results.json"), os.path.join(HERE, "param_table.tex")]
        log.finish(metrics=dict(ot_speed_yield=res["overtake_yield"]["ev_speed_ratio"]["mean"],
                                ot_speed_noyield=res["overtake_noyield"]["ev_speed_ratio"]["mean"],
                                jam_speed_yield=res["jam_yield"]["ev_speed_ratio"]["mean"],
                                jam_coll_yield=res["jam_yield"]["collisions_total"],
                                onset_median=res["bowwave"]["onset_median"]),
                   outputs=[os.path.relpath(o, ROOT) for o in outputs])
    print(json.dumps({k: v for k, v in res.items() if k not in ("overtake_onsets", "param_table")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
