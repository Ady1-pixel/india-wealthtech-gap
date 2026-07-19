"""Run the full pipeline end to end: scrape -> nlp -> scores -> model -> charts.

Usage:
    python run_pipeline.py            # full run (~2,500 reviews per app)
    python run_pipeline.py --count 200  # quick test run
"""

import argparse
import sys
import time

from src import charts, model, nlp, scores
from src import scrape as scraper
from src.config import REVIEWS_PER_APP


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=REVIEWS_PER_APP,
                        help="reviews to pull per app")
    args = parser.parse_args()

    steps = [
        ("Scraping Google Play", lambda: scraper_main(args.count)),
        ("Scoring sentiment + themes", nlp.main),
        ("Building firm experience scores", scores.main),
        ("Fitting growth model + scenarios", model.main),
        ("Rendering charts", charts.main),
    ]
    t0 = time.time()
    for label, step in steps:
        print(f"\n=== {label} ===")
        step()
    print(f"\nPipeline complete in {time.time() - t0:.0f}s. "
          "Run `streamlit run app/streamlit_app.py` to open the dashboard.")


def scraper_main(count: int) -> None:
    sys.argv = ["scrape", "--count", str(count)]
    scraper.main()


if __name__ == "__main__":
    main()
