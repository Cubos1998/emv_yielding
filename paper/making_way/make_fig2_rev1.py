"""Camera-ready Fig. 2 (force fields): vehicles drawn in red in both panels,
linear colour scale, plain contour labels. Needs only the stage-2 preset.

    python paper/making_way/make_fig2_rev1.py   # writes figs/fig_fields_rev1.{pdf,png}
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from make_figures import INK, INK2, EV_COL, COL_W
from emv.params import bluelight_params
from emv.viz import CMAP_SEQ

F_TITLE, F_BODY, F_SMALL = 9.5, 8.5, 8.0

def main(p, out=os.path.join(HERE, "figs", "fig_fields_rev1")):
    L_car, W_car = 4.6, 1.9
    def cc_mag(dx, dy):
        gx = np.maximum(np.abs(dx) - L_car, 0.05)
        gy = np.maximum(np.abs(dy) - W_car, 0.05)
        q = np.sqrt((gx / p.Bx_v) ** 2 + (gy / p.By_v) ** 2)
        mag = p.A_v * np.exp(-q) + p.A_near * np.exp(-q / p.q_near)
        d = np.hypot(dx, dy) + 1e-9
        w = p.lam_v + (1 - p.lam_v) * 0.5 * (1 + dx / d)
        return np.minimum(mag * w, p.F_cap_v)
    def emv_mag(dx, dy):
        d = np.maximum(np.hypot(dx, dy), 0.5)
        w = p.lam_ev + (1 - p.lam_ev) * 0.5 * (1 + dx / d)
        return np.minimum(p.A_ev * np.exp((p.r_ev - d) / p.B_ev), p.F_cap_ev) * w

    vmax = float(max(p.F_cap_v, p.F_cap_ev))
    norm = Normalize(vmin=0.0, vmax=vmax)
    fig = plt.figure(figsize=(COL_W, 1.62))
    axa = fig.add_axes([0.105, 0.25, 0.345, 0.62])
    axb = fig.add_axes([0.525, 0.25, 0.345, 0.62])
    cax = fig.add_axes([0.89, 0.25, 0.02, 0.62])
    panels = ((axa, cc_mag, (-14, 14, -9, 9), [0.5, 2.0], (L_car, W_car), "(a) Car–car repulsion", [(-9, -2.6), (9, 2.0)]),
              (axb, emv_mag, (-20, 52, -23, 23), [1.0, 2.0, 3.0], (5.4, 2.0), "(b) EMV point field", [(36, -12), (22, -6), (12, -3)]))
    for ax, fn, ext, lev, (L, W), title, lab in panels:
        X, Y = np.meshgrid(np.linspace(ext[0], ext[1], 460), np.linspace(ext[2], ext[3], 300))
        Z = fn(X, Y)
        im = ax.imshow(Z, extent=ext, origin="lower", aspect="equal", cmap=CMAP_SEQ,
                       interpolation="bilinear", norm=norm, zorder=0)
        cs = ax.contour(X, Y, Z, levels=lev, colors=[INK2], linewidths=0.6, zorder=2)
        ax.clabel(cs, fmt="%.1f", fontsize=F_SMALL - 1, inline=True, inline_spacing=2, colors=[INK], manual=lab)
        ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc=EV_COL, ec=INK, lw=0.4, zorder=5))
        span = ext[1] - ext[0]
        ax.annotate("", xy=(ext[0] + 0.16 * span, ext[3] * 0.8), xytext=(ext[0] + 0.05 * span, ext[3] * 0.8),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7), zorder=6)
        if ax is axa: ax.text(ext[0] + 0.18 * span, ext[3] * 0.8, "driving direction", color=INK, fontsize=F_SMALL - 1.5,
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
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.02, dpi=300)
    print(out, "vmax", vmax)

if __name__ == "__main__":
    main(bluelight_params())
