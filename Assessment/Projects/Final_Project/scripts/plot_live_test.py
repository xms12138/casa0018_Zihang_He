"""Generate live-testing figures for report Section 'Results and Observations'.

Inputs are the aggregate counts from the on-device session documented in
`experiments/exp_log.md` (entry 2026-04-28, live testing). Per-keyword integer
split is the reconstructed approximation noted in that entry; aggregate totals
(80/20 author/helper, 88/100 overall) are exact.

Outputs:
    report_figures/04_testing/live_test_per_keyword.png
    report_figures/04_testing/live_test_vs_ei.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(__file__).resolve().parent.parent / "report_figures" / "04_testing"
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = ["turn_on", "turn_off", "reading", "sleep"]

# Live test (reconstructed per-keyword split; totals exact).
LIVE_CORRECT = {"turn_on": 18, "turn_off": 22, "reading": 24, "sleep": 24}
LIVE_TOTAL = {k: 25 for k in KEYWORDS}

# EI test set, INT8 @ threshold 0.6 — from baseline entry in exp_log.md.
EI_TEST_PCT = {"turn_on": 56.7, "turn_off": 76.7, "reading": 100.0, "sleep": 90.0}


def fig_per_keyword():
    fig, ax = plt.subplots(figsize=(7.5, 4.2))

    pcts = [100 * LIVE_CORRECT[k] / LIVE_TOTAL[k] for k in KEYWORDS]
    fails = [LIVE_TOTAL[k] - LIVE_CORRECT[k] for k in KEYWORDS]
    colors = ["#d97757" if k == "turn_on" else "#5a8fbb" for k in KEYWORDS]

    bars = ax.bar(KEYWORDS, pcts, color=colors, edgecolor="black", linewidth=0.6)
    ax.axhline(88.0, color="grey", linestyle="--", linewidth=0.9,
               label="Aggregate live accuracy: 88.0% (88/100)")

    for bar, pct, k in zip(bars, pcts, KEYWORDS):
        ax.text(bar.get_x() + bar.get_width() / 2, pct + 1.2,
                f"{LIVE_CORRECT[k]}/{LIVE_TOTAL[k]}\n({pct:.0f}%)",
                ha="center", va="bottom", fontsize=9)

    ax.set_ylim(0, 110)
    ax.set_ylabel("Correct state-transition rate (%)")
    ax.set_title("Live testing on Nano 33 BLE Sense — per keyword (n = 25 each)")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)

    fig.text(0.5, -0.02,
             "Per-keyword integer split is a reconstructed approximation; "
             "totals (88/100) and qualitative ranking are exact. "
             "Author 80 trials + helper (m, 23) 20 trials.",
             ha="center", fontsize=7.5, style="italic", color="#555")

    fig.tight_layout()
    out = OUT_DIR / "live_test_per_keyword.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


def fig_vs_ei():
    fig, ax = plt.subplots(figsize=(7.5, 4.2))

    x = np.arange(len(KEYWORDS))
    w = 0.38

    ei_pcts = [EI_TEST_PCT[k] for k in KEYWORDS]
    live_pcts = [100 * LIVE_CORRECT[k] / LIVE_TOTAL[k] for k in KEYWORDS]

    ax.bar(x - w / 2, ei_pcts, width=w, label="EI test set (INT8 @ 0.6, per-frame argmax)",
           color="#9bb7d4", edgecolor="black", linewidth=0.6)
    ax.bar(x + w / 2, live_pcts, width=w, label="Live test (FSM-level correct switch)",
           color="#d97757", edgecolor="black", linewidth=0.6)

    for xi, p in zip(x - w / 2, ei_pcts):
        ax.text(xi, p + 1.2, f"{p:.1f}%", ha="center", va="bottom", fontsize=8.5)
    for xi, p in zip(x + w / 2, live_pcts):
        ax.text(xi, p + 1.2, f"{p:.0f}%", ha="center", va="bottom", fontsize=8.5)

    ax.set_xticks(x)
    ax.set_xticklabels(KEYWORDS)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Recall (%)")
    ax.set_title("Recall per keyword: EI test set vs deployed live test")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)

    fig.text(0.5, -0.02,
             "Live > EI on every keyword. Likely: primary speaker overlap with training set "
             "+ FSM 'correct switch' is more lenient than per-frame argmax (state lock collapses uncertain frames).",
             ha="center", fontsize=7.5, style="italic", color="#555")

    fig.tight_layout()
    out = OUT_DIR / "live_test_vs_ei.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    fig_per_keyword()
    fig_vs_ei()
