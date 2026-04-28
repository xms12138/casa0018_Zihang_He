"""Generate self-drawn methods diagrams as PNGs (matplotlib only).

Mermaid sources also exist in `report_figures/02_methods/diagrams.md`, but the
report is exported to PDF via the VSCode MarkdownPDF extension, which does not
render mermaid blocks. These PNGs are the canonical figures for the report.

Outputs:
    report_figures/02_methods/system_overview.png
    report_figures/02_methods/state_machine.png
    report_figures/02_methods/model_architecture.png
"""

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent.parent / "report_figures" / "02_methods"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_system_overview():
    fig, ax = plt.subplots(figsize=(12, 2.6))

    boxes = [
        ("PDM microphone\nMP34DT05\n16 kHz mono", "#dbe6f0"),
        ("MFCC DSP\n13 coef · FFT 256\n~296 ms / window", "#dbe6f0"),
        ("1D CNN (INT8)\nConv 8 → Conv 16 → Dense 6\n~4 ms / inference", "#cfe2cf"),
        ("Finite State Machine\nthreshold 0.60\n1 s state lock", "#f7e1c7"),
        ("WS2812B strip\n10 LEDs · D2 · 3.3 V\nbrightness 150/255", "#f7d3d3"),
    ]
    box_w, box_h, gap = 2.0, 1.3, 0.55
    n = len(boxes)
    total_w = n * box_w + (n - 1) * gap
    start_x = -total_w / 2

    for i, (text, color) in enumerate(boxes):
        x = start_x + i * (box_w + gap)
        rect = patches.FancyBboxPatch(
            (x, -box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.05", linewidth=1.1,
            edgecolor="black", facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(x + box_w / 2, 0, text, ha="center", va="center", fontsize=9.2)
        if i < n - 1:
            ax.annotate(
                "",
                xy=(x + box_w + gap - 0.05, 0),
                xytext=(x + box_w + 0.05, 0),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color="black"),
            )

    ax.set_xlim(start_x - 0.4, start_x + total_w + 0.4)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")
    fig.tight_layout()
    out = OUT_DIR / "system_overview.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


def make_state_machine():
    fig, ax = plt.subplots(figsize=(8.2, 6.2))

    nodes = {
        "OFF":     (0,    2.4,  "#9c9c9c", "white"),
        "GENERAL": (-3.0, 0.0,  "#3aa6ff", "white"),
        "READING": (3.0,  0.0,  "#ffffff", "black"),
        "SLEEP":   (0,   -2.4,  "#ff5023", "white"),
    }
    box_w, box_h = 1.7, 0.75

    for name, (x, y, fc, tc) in nodes.items():
        rect = patches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.05", linewidth=1.5,
            edgecolor="black", facecolor=fc,
        )
        ax.add_patch(rect)
        ax.text(x, y, name, ha="center", va="center",
                fontsize=11, fontweight="bold", color=tc)

    def edge(a, b, label, curved=0.0, lbl_dx=0, lbl_dy=0):
        x1, y1, *_ = nodes[a]
        x2, y2, *_ = nodes[b]
        dx, dy = x2 - x1, y2 - y1
        d = (dx ** 2 + dy ** 2) ** 0.5
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * 0.95, y1 + uy * 0.45
        ex, ey = x2 - ux * 0.95, y2 - uy * 0.45
        ax.annotate(
            "", xy=(ex, ey), xytext=(sx, sy),
            arrowprops=dict(arrowstyle="-|>", lw=1.3,
                            connectionstyle=f"arc3,rad={curved}"),
        )
        mx, my = (sx + ex) / 2 + lbl_dx, (sy + ey) / 2 + lbl_dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=9.2,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="#bbb", alpha=0.95))

    edge("OFF", "GENERAL", "turn_on", curved=-0.18, lbl_dx=-0.55, lbl_dy=0.05)
    edge("GENERAL", "OFF", "turn_off (any → OFF)", curved=-0.18, lbl_dx=0.85, lbl_dy=0.0)
    edge("READING", "OFF", "", curved=-0.18)
    edge("SLEEP",   "OFF", "", curved=0.18)
    edge("GENERAL", "READING", "reading", curved=0.18, lbl_dy=0.4)
    edge("GENERAL", "SLEEP",   "sleep",   curved=-0.18, lbl_dx=-0.5, lbl_dy=-0.1)
    edge("READING", "SLEEP",   "sleep",   curved=-0.18, lbl_dx=0.55, lbl_dy=0.1)
    edge("SLEEP",   "READING", "reading", curved=-0.18, lbl_dx=-0.55, lbl_dy=-0.1)

    ax.set_xlim(-5.0, 5.0)
    ax.set_ylim(-3.6, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, 3.3, "EchoLume FSM (threshold 0.60, 1 s state lock)",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(0, -3.4,
            "noise / unknown / sub-threshold predictions: ignored (no transition)",
            ha="center", fontsize=8.8, style="italic", color="#555")
    fig.tight_layout()
    out = OUT_DIR / "state_machine.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


def make_model_architecture():
    fig, ax = plt.subplots(figsize=(5.6, 8.4))

    layers = [
        ("Input · 637 features (flat)",         "#dbe6f0"),
        ("Reshape · 13 columns\n(time × cepstral)", "#dbe6f0"),
        ("Conv1D · 8 filters · k=3 · ReLU",     "#cfe2cf"),
        ("Dropout 0.25",                        "#eeeeee"),
        ("Conv1D · 16 filters · k=3 · ReLU",    "#cfe2cf"),
        ("Dropout 0.25",                        "#eeeeee"),
        ("Flatten",                             "#dbe6f0"),
        ("Dense 6 · softmax",                   "#f7e1c7"),
    ]
    box_w, box_h, gap = 4.4, 0.75, 0.3
    n = len(layers)
    total_h = n * box_h + (n - 1) * gap
    start_y = total_h / 2

    for i, (text, color) in enumerate(layers):
        y = start_y - i * (box_h + gap) - box_h
        rect = patches.FancyBboxPatch(
            (-box_w / 2, y), box_w, box_h,
            boxstyle="round,pad=0.05", linewidth=1.0,
            edgecolor="black", facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(0, y + box_h / 2, text, ha="center", va="center", fontsize=10)
        if i < n - 1:
            ax.annotate(
                "", xy=(0, y - gap + 0.06), xytext=(0, y),
                arrowprops=dict(arrowstyle="-|>", lw=1.2),
            )

    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-total_h / 2 - 0.7, total_h / 2 + 0.7)
    ax.axis("off")
    ax.text(0, total_h / 2 + 0.5, "Baseline 1D CNN (INT8)",
            ha="center", fontsize=11.5, fontweight="bold")
    ax.text(0, -total_h / 2 - 0.5,
            "Cortex-M4F estimate: ~4 ms inference · ~12.5 KB RAM · ~46.4 KB flash",
            ha="center", fontsize=8.8, style="italic", color="#555")
    fig.tight_layout()
    out = OUT_DIR / "model_architecture.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    make_system_overview()
    make_state_machine()
    make_model_architecture()
