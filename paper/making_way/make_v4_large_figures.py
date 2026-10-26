"""Larger-font redraws of Fig. 1 (pipeline) and Fig. 2 (force fields) for the camera-ready paper (Fig. 1 is used as printed; Fig. 2 was
later replaced by make_fig2_rev1.py).

Same content as fig_pipeline(..., name="fig1_pipeline_v4") and fig_fields() in
make_figures.py, re-laid out so every label is legible at print size (body text
of the paper is 10 pt; labels here are 7.5-9.5 pt). No simulation is run: both
figures only need the stage-2 parameter preset.

    python paper/making_way/make_v4_large_figures.py   # writes figs/*_large.{pdf,png}
"""
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.pyplot as plt

from make_figures import _save, INK, INK2, EV_COL, CAT_LIGHT, COL_W, TXT_W
from emv.params import bluelight_params
from emv.viz import CMAP_SEQ

# font sizes (pt) shared by both figures
F_TITLE, F_BODY, F_ZONE, F_SMALL = 9.5, 8.5, 9.0, 8.0


# ------------------------------------------------------------------ Fig. 1
def fig_pipeline_large(name="fig1_pipeline_v4_large"):
    """x runs 0-100 across the text width; y is in points so text spacing is exact."""
    T_TOP, L_TOP, L_STEP, PAD = 3.8, 15.0, 10.2, 3.0     # title / first-line offset, line pitch, gap

    def bh(n):                                           # height of a box with n body lines
        return L_TOP + (n - 1) * L_STEP + 11.5

    # vertical plan, bottom-up (points)
    S_Y, S_H = 1.0 + PAD, bh(2)                          # stage boxes
    Z4_H = S_H + 2 * PAD                                 # zone 4
    Z0 = 1.0 + Z4_H + 17.0                               # upper zones start above the zone-4 label
    lo_h, mid_h, hi_h = bh(1), bh(2), bh(2)              # rows of zones 1 and 3
    lo_y = Z0 + PAD; mid_y = lo_y + lo_h + PAD; hi_y = mid_y + mid_h + PAD
    ZH = hi_y + hi_h + PAD - Z0
    m_y, m_h = lo_y, 17.0                                # step 5 (maths) box
    f_y, f_h = m_y + m_h + 4.0, bh(2)                    # step 4 (forces)
    r_y = f_y + f_h + 4.0; r_h = Z0 + ZH - PAD - r_y     # steps 1-3
    H = Z0 + ZH + 14.0

    fig = plt.figure(figsize=(TXT_W, H / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, H); ax.axis("off")

    def box(x, y, w, h, title, lines, head=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                    fc="#fcfcfb", ec=INK2, lw=0.7, zorder=2, mutation_aspect=5.0))
        if head:
            ax.add_patch(Rectangle((x, y + h - 2.6), w, 2.6, fc=head, ec="none", zorder=3))
        ax.text(x + 0.9, y + h - T_TOP, title, fontsize=F_TITLE, fontweight="bold",
                color=INK, va="top", zorder=4)
        for k, ln in enumerate(lines):
            ax.text(x + 0.9, y + h - L_TOP - k * L_STEP, ln, fontsize=F_BODY, color=INK2,
                    va="top", zorder=4)

    def arrow(x0, y0, x1, y1, col=INK2, lw=0.9):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=5,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                    shrinkA=0, shrinkB=0, mutation_scale=8))

    def zone(x, y, w, h, fill):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                    fc=fill, ec="none", zorder=1, mutation_aspect=5.0))

    def label(x, y, text, ha="left"):
        ax.text(x, y, text, fontsize=F_ZONE, fontweight="bold", color=INK2, va="bottom", ha=ha)

    top = Z0 + ZH + 1.5

    # zone 1: inputs
    zone(0.5, Z0, 20.3, ZH, "#f2f1ec"); label(1.3, top, "(1) INPUTS")
    box(1.2, hi_y, 18.9, hi_h, "Parameters", ["presets: defaults,", "stage 1, stage 2 (Table I)"])
    box(1.2, mid_y, 18.9, mid_h, "Scenarios", ["motorway overtake,", "jam, highD-like"])
    box(1.2, lo_y, 18.9, lo_h, "Empirical data", ["highD, dashcam passages"], head=CAT_LIGHT["blue"])

    # zone 2: per-step core
    zone(21.9, Z0, 52.3, ZH, "#f2f1ec"); label(22.7, top, "(2) SIMULATION CORE: one step every 0.05 s")
    box(22.6, r_y, 15.9, r_h, "1  Corridor", ["project the EMV path", "ahead; sideways", "distance d from it"])
    box(40.1, r_y, 15.9, r_h, "2  Perception", ["unaware, noticed,", "yielding, hold;", "urgency u"], head=CAT_LIGHT["yellow"])
    box(57.6, r_y, 15.9, r_h, "3  Lane choice", ["commit when the", "incentive exceeds", "the lane barrier"], head=CAT_LIGHT["blue"])
    ra = r_y + r_h - L_TOP - L_STEP - 4.0
    arrow(38.5, ra, 40.1, ra); arrow(56.0, ra, 57.6, ra)
    box(22.6, f_y, 50.9, f_h, "4  Forces (accelerations)",
        ["drive, car-car, lane keeping, lane incentive  |  EMV point field,", "corridor field (gated by u)"],
        head=CAT_LIGHT["red"])
    arrow(65.5, r_y, 65.5, f_y + f_h)
    ax.add_patch(FancyBboxPatch((22.6, m_y), 50.9, m_h, boxstyle="round,pad=0,rounding_size=0.8",
                                fc=INK, ec="none", zorder=2, mutation_aspect=5.0))
    ax.text(23.6, m_y + m_h / 2, r"5  $a_x = a^{\rm drive} + \min(F^{\rm social}_x,\ a^{\rm IDM})$,  clamp, semi-implicit Euler",
            fontsize=F_BODY, color="#fcfcfb", va="center", zorder=4)
    arrow(48.0, f_y, 48.0, m_y + m_h)

    # zone 3: measurement & theory (label right-aligned: it is wider than the zone)
    zone(75.5, Z0, 24.0, ZH, "#f2f1ec"); label(99.5, top, "(3) MEASUREMENT & THEORY", ha="right")
    box(76.2, hi_y, 22.6, hi_h, "Trajectories and metrics", ["progress, safety, timing;", "same detector as highD"])
    box(76.2, mid_y, 22.6, mid_h, "Per-term influence", ["force budget, ablations"])
    box(76.2, lo_y, 22.6, lo_h, "Depinning theory", [r"escape if $A_c u > a_{\rm pin}^{\rm eff}$; $d^*$"])
    arrow(73.5, m_y + m_h / 2, 76.2, hi_y + hi_h / 2)
    arrow(20.1, hi_y + hi_h / 2, 22.6, hi_y + hi_h / 2)
    arrow(20.1, f_y + f_h / 2, 22.6, f_y + f_h / 2)

    # zone 4: identification
    zone(0.5, 1.0, 99.0, Z4_H, "#eaf6f0")
    label(47.0, 1.0 + Z4_H + 2.5, "(4) TWO-STAGE IDENTIFICATION: Latin hypercube + Nelder-Mead", ha="center")
    box(1.2, S_Y, 44.3, S_H, "Stage 1: ordinary traffic, EMV absent",
        ["19 parameters (car following 8, lateral 7, lane changing 4)", "fitted to highD, free-flow + dense"],
        head=CAT_LIGHT["blue"])
    box(54.5, S_Y, 44.3, S_H, "Stage 2: add the emergency vehicle",
        [r"stage 1 frozen; only $A_{\rm emv}$, $B_{\rm emv}$, $A_c$, $B_c$ fitted",
         "to the dashcam behaviour fingerprint"], head=CAT_LIGHT["red"])
    sm = S_Y + S_H / 2 - 2.0
    arrow(45.5, sm, 54.5, sm, col=CAT_LIGHT["aqua"], lw=1.1)
    ax.text(50.0, sm + 2.5, "freeze", fontsize=F_SMALL, color=INK2, ha="center", va="bottom")
    mid_gap = 1.0 + Z4_H + (Z0 - 1.0 - Z4_H) / 2
    arrow(8.0, lo_y, 8.0, S_Y + S_H, col=CAT_LIGHT["blue"])
    ax.text(9.0, mid_gap, "targets", fontsize=F_SMALL, color=INK2, va="center")
    arrow(92.0, Z0, 92.0, S_Y + S_H, col=CAT_LIGHT["aqua"])
    ax.text(91.0, mid_gap, "simulated observables", fontsize=F_SMALL, color=INK2, va="center", ha="right")
    return _save(fig, name)


# ------------------------------------------------------------------ Fig. 2
def fig_fields_large(p, name="fig_fields_v4_large"):
    """Same fields, contours and colour scale as make_figures.fig_fields."""
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
    fig = plt.figure(figsize=(COL_W, 1.62))
    axa = fig.add_axes([0.105, 0.25, 0.345, 0.62])
    axb = fig.add_axes([0.525, 0.25, 0.345, 0.62])
    cax = fig.add_axes([0.89, 0.25, 0.02, 0.62])
    panels = ((axa, cc_mag, (-14, 14, -9, 9), [0.2, 1.0], CAT_LIGHT["blue"], (L_car, W_car),
               "(a) Car–car repulsion", [(-3, -4.3), (-6, 2.9)]),
              (axb, emv_mag, (-20, 52, -23, 23), [0.3, 1.0, 3.0], EV_COL, (5.4, 2.0),
               "(b) EMV point field", [(-14, 8), (24, -14), (9, -2)]))
    for ax, fn, ext, lev, col, (L, W), title, lab_pos in panels:
        X, Y = np.meshgrid(np.linspace(ext[0], ext[1], 460), np.linspace(ext[2], ext[3], 300))
        Z = fn(X, Y)
        im = ax.imshow(Z, extent=ext, origin="lower", aspect="equal", cmap=CMAP_SEQ,
                       interpolation="bilinear", norm=norm, zorder=0)
        cs = ax.contour(X, Y, Z, levels=lev, colors=[INK2], linewidths=0.6, zorder=2)
        ax.clabel(cs, fmt="%.2g", fontsize=F_SMALL - 0.5, inline_spacing=1.5, manual=lab_pos)
        ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc=col, ec=INK, lw=0.4, zorder=5))
        span = ext[1] - ext[0]
        ax.annotate("", xy=(ext[0] + 0.24 * span, ext[3] * 0.74), xytext=(ext[0] + 0.05 * span, ext[3] * 0.74),
                    arrowprops=dict(arrowstyle="-|>", color="white", lw=0.9, mutation_scale=7), zorder=6)
        ax.text(ext[0] + 0.26 * span, ext[3] * 0.74, "driving direction", color="white", fontsize=F_SMALL - 0.5,
                va="center", zorder=6)
        ax.set_title(title, loc="left", fontsize=F_TITLE - 0.5, pad=2)
        ax.tick_params(labelsize=F_SMALL, length=2, pad=1)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
    axa.set_xlabel("Longitudinal offset (m)", fontsize=F_BODY, labelpad=1)
    axb.set_xlabel("Longitudinal offset (m)", fontsize=F_BODY, labelpad=1)
    axa.set_ylabel("Lateral offset (m)", fontsize=F_BODY, labelpad=1)
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(labelsize=F_SMALL, length=1.5, pad=1)
    cb.set_label(r"Acceleration (m/s$^2$)", fontsize=F_BODY - 0.5, labelpad=1)
    cb.outline.set_linewidth(0.4)
    return _save(fig, name)


if __name__ == "__main__":
    for path in fig_pipeline_large() + fig_fields_large(bluelight_params()):
        print(path)
