"""Scrape Google Play metadata and user reviews for every app in the roster.

Usage:
    python -m src.scrape            # full pull (REVIEWS_PER_APP per app)
    python -m src.scrape --count 200  # smaller test pull
"""

import argparse
import sys
import time

import pandas as pd
from google_play_scraper import Sort, app, reviews

from src.config import APPS, COUNTRY, DATA_RAW, LANG, REVIEWS_PER_APP


def scrape_metadata() -> pd.DataFrame:
    rows = []
    for entry in APPS:
        meta = app(entry["app_id"], lang=LANG, country=COUNTRY)
        rows.append(
            {
                "firm": entry["firm"],
                "app_id": entry["app_id"],
                "segment": entry["segment"],
                "category": entry["category"],
                "app_title": meta["title"],
                "play_rating": meta["score"],
                "ratings_count": meta["ratings"],
                "reviews_count": meta["reviews"],
                "installs": meta["installs"],
                "histogram_1_to_5": meta["histogram"],
                "last_updated": meta.get("lastUpdatedOn"),
            }
        )
        print(f"[meta] {entry['firm']}: rating={meta['score']:.2f}, ratings={meta['ratings']:,}")
    return pd.DataFrame(rows)


def scrape_reviews(count: int) -> pd.DataFrame:
    frames = []
    for entry in APPS:
        got, token, batch_errors = [], None, 0
        while len(got) < count:
            try:
                batch, token = reviews(
                    entry["app_id"],
                    lang=LANG,
                    country=COUNTRY,
                    sort=Sort.NEWEST,
                    count=min(200, count - len(got)),
                    continuation_token=token,
                )
            except Exception as exc:  # transient network/parse hiccups: retry a few times
                batch_errors += 1
                if batch_errors > 3:
                    print(f"[reviews] {entry['firm']}: giving up after {batch_errors} errors ({exc})")
                    break
                time.sleep(2)
                continue
            if not batch:
                break
            got.extend(batch)
            if token is None:
                break
        df = pd.DataFrame(got)
        if df.empty:
            print(f"[reviews] {entry['firm']}: NO REVIEWS PULLED", file=sys.stderr)
            continue
        df = df[["reviewId", "content", "score", "thumbsUpCount", "at", "appVersion"]]
        df.insert(0, "firm", entry["firm"])
        df.insert(1, "category", entry["category"])
        df.insert(2, "segment", entry["segment"])
        frames.append(df)
        print(f"[reviews] {entry['firm']}: {len(df):,} reviews pulled")
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=REVIEWS_PER_APP)
    args = parser.parse_args()

    DATA_RAW.mkdir(parents=True, exist_ok=True)

    meta = scrape_metadata()
    meta.to_csv(DATA_RAW / "app_metadata.csv", index=False)

    revs = scrape_reviews(args.count)
    revs.to_csv(DATA_RAW / "reviews.csv", index=False)
    print(f"\nSaved {len(meta)} apps and {len(revs):,} reviews to {DATA_RAW}")


if __name__ == "__main__":
    main()
