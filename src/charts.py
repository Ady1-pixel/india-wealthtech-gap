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


def dress(fig, ax, source):
    fig.text(0.012, 0.982, "INDIA WEALTHTECH \u00b7 SECTOR NOTE \u00b7 JULY 2026",
             fontsize=7.5, color=MARIGOLD, fontfamily=MONO, va="top")
    fig.text(0.012, 0.012, source, fontsize=7.5, color=INK_2, fontfamily=MONO, va="bottom")


def color_for(cat: str) -> str:
    return FINTECH if cat == "fintech" else INCUMBENT


def legend(ax):
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=FINTECH, label="Fintech-native"),
        plt.Rectangle((0, 0), 1, 1, color=INCUMBENT, label="Incumbent"),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=9)


def chart_experience_ranking(scores: pd.DataFrame) -> None:
    df = scores.sort_values("experience_score")
    fig, ax = plt.subplots(figsize=(9, 6.5))
    bars = ax.barh(
        df["firm"], df["experience_score"],
        color=[color_for(c) for c in df["category"]], height=0.62,
    )
    for bar, v in zip(bars, df["experience_score"]):
        ax.text(v + 0.7, bar.get_y() + bar.get_height() / 2, f"{v:.0f}",
                va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Digital Experience Score (0–100)")
    ax.set_title(
        "Fintech-native apps hold the top of the experience table",
        loc="left", fontsize=14, fontweight="bold", color=INK, pad=16, fontfamily=SERIF,
    )
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, ax, "SOURCE: 44,200 GOOGLE PLAY REVIEWS (IN STOREFRONT), SCRAPED JULY 2026")
    fig.savefig(OUTPUTS / "experience_ranking.png", dpi=180)
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
    ax.set_title(
        "The only brokers that grew are near the top of the experience table",
        loc="left", fontsize=14, fontweight="bold", color=INK, pad=16, fontfamily=SERIF,
    )
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, ax, "SOURCE: GOOGLE PLAY REVIEWS + NSE ACTIVE CLIENTS VIA CHITTORGARH / STARTUPTALKY")
    fig.savefig(OUTPUTS / "score_vs_growth.png", dpi=180)
    plt.close(fig)


def chart_pain_rates(scores: pd.DataFrame) -> None:
    df = scores.sort_values("pain_rate", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    bars = ax.barh(
        df["firm"], 100 * df["pain_rate"],
        color=[color_for(c) for c in df["category"]], height=0.62,
    )
    for bar, v in zip(bars, 100 * df["pain_rate"]):
        ax.text(v + 0.25, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%",
                va="center", fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("Share of reviews that are 1–2 stars and cite UI/UX, crashes, KYC, or support")
    ax.set_title(
        "Where the experience actively hurts: pain rate by app",
        loc="left", fontsize=14, fontweight="bold", color=INK, pad=16, fontfamily=SERIF,
    )
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, ax, "SOURCE: 44,200 GOOGLE PLAY REVIEWS, THEME-TAGGED 1-2 STAR SHARE")
    fig.savefig(OUTPUTS / "pain_rates.png", dpi=180)
    plt.close(fig)


def chart_ai_whitespace(scores: pd.DataFrame) -> None:
    df = scores.sort_values("ai_mention_rate", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    bars = ax.barh(
        df["firm"], 100 * df["ai_mention_rate"],
        color=[color_for(c) for c in df["category"]], height=0.62,
    )
    for bar, v in zip(bars, 100 * df["ai_mention_rate"]):
        ax.text(v + 0.02, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%",
                va="center", fontsize=9, color=INK)
    ax.set_xlabel("Share of reviews mentioning AI / advisory / smart features")
    ax.set_title(
        "AI is barely part of the user conversation yet: the whitespace",
        loc="left", fontsize=14, fontweight="bold", color=INK, pad=16, fontfamily=SERIF,
    )
    legend(ax)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    dress(fig, ax, "SOURCE: 44,200 GOOGLE PLAY REVIEWS, AI/ADVISORY KEYWORD MENTIONS")
    fig.savefig(OUTPUTS / "ai_whitespace.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    scores = pd.read_csv(DATA_PROCESSED / "firm_scores.csv")
    panel = pd.read_csv(DATA_PROCESSED / "broker_panel.csv")
    with open(DATA_PROCESSED / "model_results.json") as f:
        model = json.load(f)

    chart_experience_ranking(scores)
    chart_score_vs_growth(panel, model)
    chart_pain_rates(scores)
    chart_ai_whitespace(scores)
    print(f"Charts saved to {OUTPUTS}")


if __name__ == "__main__":
    main()
