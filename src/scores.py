"""Aggregate review-level scores into a per-firm Digital Experience Score (DES).

DES (0-100) = 50% Play Store rating + 30% review sentiment + 20% pain-free rate.

- rating: the app's live Play Store score (broad, high-n signal)
- sentiment: mean VADER compound over scraped recent reviews (what users say now)
- pain rate: share of reviews that are 1-2 stars AND mention a pain theme
  (UI/UX, performance, onboarding/KYC, or support), the "actively hurting" share

Usage:
    python -m src.scores
"""

import pandas as pd

from src.config import DATA_PROCESSED, DATA_RAW, TOPIC_LEXICONS

PAIN_THEMES = ["ui_ux", "performance", "onboarding_kyc", "customer_support"]

WEIGHT_RATING = 0.5
WEIGHT_SENTIMENT = 0.3
WEIGHT_PAIN_FREE = 0.2


def main() -> None:
    meta = pd.read_csv(DATA_RAW / "app_metadata.csv")
    reviews = pd.read_csv(DATA_PROCESSED / "reviews_scored.csv")

    rows = []
    for firm, grp in reviews.groupby("firm"):
        m = meta.loc[meta["firm"] == firm].iloc[0]
        negative = grp["score"] <= 2
        painful = grp[PAIN_THEMES].any(axis=1)
        pain_rate = float((negative & painful).mean())
        mean_sent = float(grp["sentiment"].mean())

        des = 100 * (
            WEIGHT_RATING * (m["play_rating"] / 5)
            + WEIGHT_SENTIMENT * ((mean_sent + 1) / 2)
            + WEIGHT_PAIN_FREE * (1 - pain_rate)
        )

        ai_mask = grp["ai_features"]
        row = {
            "firm": firm,
            "category": grp["category"].iloc[0],
            "segment": grp["segment"].iloc[0],
            "play_rating": m["play_rating"],
            "ratings_count": m["ratings_count"],
            "n_reviews_analyzed": len(grp),
            "mean_sentiment": round(mean_sent, 4),
            "pain_rate": round(pain_rate, 4),
            "experience_score": round(des, 1),
            "ai_mention_rate": round(float(ai_mask.mean()), 4),
            "ai_sentiment": round(float(grp.loc[ai_mask, "sentiment"].mean()), 4)
            if ai_mask.any()
            else None,
        }
        # theme-level complaint rates (negative reviews mentioning the theme)
        for theme in TOPIC_LEXICONS:
            row[f"neg_{theme}_rate"] = round(float((negative & grp[theme]).mean()), 4)
        rows.append(row)

    scores = pd.DataFrame(rows).sort_values("experience_score", ascending=False)
    scores.to_csv(DATA_PROCESSED / "firm_scores.csv", index=False)
    print(scores[["firm", "category", "play_rating", "mean_sentiment", "pain_rate", "experience_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
