"""Static charts for the README, saved to outputs/.

Usage:
    python -m src.charts
"""

import json

import matplotlib.pyplot as plt
import pandas as pd

from src.config import DATA_PROCESSED, OUTPUTS

FINTECH = "#2a78d6"
INCUMBENT = "#eb6834"
MARIGOLD = "#b57a00"
INK = "#1c1a16"
INK_2 = "#6b675e"
SURFACE = "#faf8f3"
SERIF = "Georgia"
MONO = "Menlo"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": MONO,
        "font.size": 9.5,
        "text.color": INK,
        "axes.edgecolor": INK_2,
        "axes.labelcolor": INK_2,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": False,
    }
)


def color_for(cat: str) -> str:
    return FINTECH if cat == "fintech" else INCUMBENT


def legend(ax) -> None:
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=FINTECH, label="Fintech-native"),
        plt.Rectangle((0, 0), 1, 1, color=INCUMBENT, label="Incumbent"),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=9)


def dress(fig, source: str) -> None:
    """Sector-note framing: eyebrow on top, source line at the bottom."""
    fig.text(0.012, 0.982, "INDIA WEALTHTECH · SECTOR NOTE · JULY 2026",
             fontsize=7.5, color=MARIGOLD, fontfamily=MONO, va="top")
    fig.text(0.012, 0.012, source, fontsize=7.5, color=INK_2, fontfamily=MONO, va="bottom")


def hbar(df: pd.DataFrame, value_col: str, title: str, xlabel: str, source: str,
         fname: str, value_fmt=lambda v: f"{v:.0f}", label_pad: float = 0.7,
         xlim: tuple | None = None, top_first: bool = True) -> None:
    """One ranked horizontal bar chart, colored by firm category."""
    df = df.sort_values(value_col, ascending=not top_first)
    if top_first:
        df = df.iloc[::-1]  # barh draws bottom-up; flip so rank 1 lands on top
    fig, ax = plt.subplots(figsize=(9, 6.5))
    bars = ax.barh(df["firm"], df[value_col],
                   color=[color_for(c) for c in df["category"]], height=0.62)
    for bar, v in zip(bars, df[value_col]):
        ax.text(v + label_pad, bar.get_y() + bar.get_height() / 2, value_fmt(v),
                va="center", fontsize=9, color=INK)
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=INK,
                 pad=16, fontfamily=SERIF)
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, source)
    fig.savefig(OUTPUTS / fname, dpi=180)
    plt.close(fig)


def chart_score_vs_growth(panel: pd.DataFrame, model: dict) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    for _, r in panel.iterrows():
        ax.scatter(r["experience_score"], r["growth_pct"],
                   s=90, color=color_for(r["category"]), zorder=3)
        ax.annotate(r["firm"], (r["experience_score"], r["growth_pct"]),
                    xytext=(6, 5), textcoords="offset points",
                    fontsize=8.5, color=INK_2)
    xs = pd.Series([panel["experience_score"].min() - 1, panel["experience_score"].max() + 1])
    ax.plot(xs, model["intercept"] + model["slope_pp_per_point"] * xs,
            color=INK_2, lw=2, ls="--", zorder=2)
    ax.axhline(0, color=INK_2, lw=0.8, alpha=0.5)
    ax.set_xlabel("Digital Experience Score (0–100)")
    ax.set_ylabel("Active-client growth, mid-2025 → June 2026 (%)")
    ax.set_title("The only brokers that grew are near the top of the experience table",
                 loc="left", fontsize=14, fontweight="bold", color=INK, pad=16,
                 fontfamily=SERIF)
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, "SOURCE: GOOGLE PLAY REVIEWS + NSE ACTIVE CLIENTS VIA CHITTORGARH / STARTUPTALKY")
    fig.savefig(OUTPUTS / "score_vs_growth.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    scores = pd.read_csv(DATA_PROCESSED / "firm_scores.csv")
    panel = pd.read_csv(DATA_PROCESSED / "broker_panel.csv")
    with open(DATA_PROCESSED / "model_results.json") as f:
        model = json.load(f)

    hbar(scores, "experience_score",
         "Fintech-native apps hold the top of the experience table",
         "Digital Experience Score (0–100)",
         "SOURCE: 44,200 GOOGLE PLAY REVIEWS (IN STOREFRONT), SCRAPED JULY 2026",
         "experience_ranking.png", xlim=(0, 100))

    chart_score_vs_growth(panel, model)

    pain = scores.assign(pain_pct=100 * scores["pain_rate"])
    hbar(pain, "pain_pct",
         "Where the experience actively hurts: pain rate by app",
         "Share of reviews that are 1–2 stars and cite UI/UX, crashes, KYC, or support",
         "SOURCE: 44,200 GOOGLE PLAY REVIEWS, THEME-TAGGED 1-2 STAR SHARE",
         "pain_rates.png", value_fmt=lambda v: f"{v:.1f}%", label_pad=0.25)

    ai = scores.assign(ai_pct=100 * scores["ai_mention_rate"])
    hbar(ai, "ai_pct",
         "AI is barely part of the user conversation yet: the whitespace",
         "Share of reviews mentioning AI / advisory / smart features",
         "SOURCE: 44,200 GOOGLE PLAY REVIEWS, AI/ADVISORY KEYWORD MENTIONS",
         "ai_whitespace.png", value_fmt=lambda v: f"{v:.1f}%", label_pad=0.02,
         top_first=False)

    print(f"Charts saved to {OUTPUTS}")


if __name__ == "__main__":
    main()
