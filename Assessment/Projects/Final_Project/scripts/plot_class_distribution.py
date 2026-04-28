"""Generate the dataset class distribution bar chart for report Section 'Data'.

Counts come from the project dataset summary (CLAUDE.md §5). Total = 1175 samples
across 6 classes; train/test split is 80/20 by EI default.
"""

from pathlib import Path

import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent.parent / "report_figures" / "01_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = [
    ("turn_on",  150, "self-recorded"),
    ("turn_off", 150, "self-recorded"),
    ("reading",  150, "self-recorded"),
    ("sleep",    150, "self-recorded"),
    ("noise",    175, "MS-SNSD (Reddy 2019)"),
    ("unknown",  250, "Speech Commands V2 (Warden 2018)"),
]

ACTION_COLOR = "#5a8fbb"
DISTRACTOR_COLOR = "#9c9c9c"


def main():
    labels = [c[0] for c in CLASSES]
    counts = [c[1] for c in CLASSES]
    sources = [c[2] for c in CLASSES]
    colors = [ACTION_COLOR if s == "self-recorded" else DISTRACTOR_COLOR for s in sources]

    fig, ax = plt.subplots(figsize=(8, 4.4))
    bars = ax.bar(labels, counts, color=colors, edgecolor="black", linewidth=0.6)

    total = sum(counts)
    for bar, n in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, n + 4,
                f"{n}\n({100 * n / total:.1f}%)",
                ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("Number of samples")
    ax.set_ylim(0, max(counts) * 1.18)
    ax.set_title(f"EchoLume dataset class distribution (n = {total})")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=ACTION_COLOR, edgecolor="black", linewidth=0.6,
                      label="Action keywords (self-recorded)"),
        plt.Rectangle((0, 0), 1, 1, color=DISTRACTOR_COLOR, edgecolor="black", linewidth=0.6,
                      label="Distractor classes (public datasets)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=9, framealpha=0.95)

    fig.text(0.5, -0.02,
             "noise: MS-SNSD via Edge Impulse public datasets (Reddy et al. 2019). "
             "unknown: Google Speech Commands V2 subset (Warden 2018). "
             "Train/test split 80/20.",
             ha="center", fontsize=7.5, style="italic", color="#555")

    fig.tight_layout()
    out = OUT_DIR / "class_distribution.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
