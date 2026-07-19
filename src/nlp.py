"""Score every review: sentiment (VADER) + theme tags from keyword lexicons.

Usage:
    python -m src.nlp
"""

import re

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.config import DATA_PROCESSED, DATA_RAW, TOPIC_LEXICONS

# Words like "ai" and "ui" need word boundaries so "wait" or "guide" don't match.
_COMPILED = {
    theme: re.compile(r"\b(" + "|".join(re.escape(k) for k in kws) + r")\b", re.IGNORECASE)
    for theme, kws in TOPIC_LEXICONS.items()
}


def tag_themes(text: str) -> dict:
    return {theme: bool(rx.search(text)) for theme, rx in _COMPILED.items()}


def main() -> None:
    reviews = pd.read_csv(DATA_RAW / "reviews.csv")
    reviews = reviews.dropna(subset=["content"]).copy()
    reviews["content"] = reviews["content"].astype(str)

    analyzer = SentimentIntensityAnalyzer()
    reviews["sentiment"] = reviews["content"].map(
        lambda t: analyzer.polarity_scores(t)["compound"]
    )

    tags = pd.DataFrame([tag_themes(t) for t in reviews["content"]], index=reviews.index)
    scored = pd.concat([reviews, tags], axis=1)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    scored.to_csv(DATA_PROCESSED / "reviews_scored.csv", index=False)

    n_themes = {t: int(scored[t].sum()) for t in TOPIC_LEXICONS}
    print(f"Scored {len(scored):,} reviews. Theme hits: {n_themes}")


if __name__ == "__main__":
    main()
