"""Link experience scores to client growth, then run 'what if' scenarios.

Cross-sectional model: YoY NSE active-client growth (~mid-2025 to June 2026)
regressed on the Digital Experience Score across 13 brokers. n is small, so
this is presented as directional evidence with a bootstrap confidence band,
not causal inference. The scenario engine treats the fitted slope as an
adjustable elasticity assumption.

Usage:
    python -m src.model
"""

import json

import numpy as np
import pandas as pd
from scipy import stats

from src.config import DATA_PROCESSED, ROOT

RNG = np.random.default_rng(42)
N_BOOT = 5000

# Scenario assumptions (documented in README; adjustable in the dashboard)
TARGET_SCORE_QUANTILE = 0.75  # "closing the gap" = reaching the 75th percentile score
REVENUE_PER_CLIENT_INR = 3000  # blended annual revenue per active client (assumption)


def fit(df: pd.DataFrame) -> dict:
    x, y = df["experience_score"].values, df["growth_pct"].values
    res = stats.linregress(x, y)

    slopes = []
    idx = np.arange(len(df))
    for _ in range(N_BOOT):
        s = RNG.choice(idx, size=len(idx), replace=True)
        if np.ptp(x[s]) == 0:
            continue
        slopes.append(stats.linregress(x[s], y[s]).slope)
    lo, hi = np.percentile(slopes, [2.5, 97.5])

    return {
        "slope_pp_per_point": res.slope,
        "intercept": res.intercept,
        "r": res.rvalue,
        "r_squared": res.rvalue**2,
        "p_value": res.pvalue,
        "slope_ci_95": [lo, hi],
        "n_firms": len(df),
    }


def scenarios(df: pd.DataFrame, slope: float, target_score: float) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        gap = max(0.0, target_score - r["experience_score"])
        uplift_pp = slope * gap  # extra YoY growth, percentage points
        extra_clients = r["active_clients_2026"] * uplift_pp / 100
        rows.append(
            {
                "firm": r["firm"],
                "category": r["category"],
                "experience_score": r["experience_score"],
                "score_gap_to_target": round(gap, 1),
                "actual_growth_pct": round(r["growth_pct"], 2),
                "modeled_uplift_pp": round(uplift_pp, 2),
                "projected_extra_clients_1yr": int(extra_clients),
                "projected_extra_revenue_inr_cr": round(
                    extra_clients * REVENUE_PER_CLIENT_INR / 1e7, 1
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("projected_extra_clients_1yr", ascending=False)


def main() -> None:
    scores = pd.read_csv(DATA_PROCESSED / "firm_scores.csv")
    clients = pd.read_csv(ROOT / "data" / "nse_active_clients.csv")

    df = scores.merge(clients, on="firm", how="inner")
    df["growth_pct"] = 100 * (
        df["active_clients_2026"] / df["active_clients_2025"] - 1
    )

    result = fit(df)
    target = float(df["experience_score"].quantile(TARGET_SCORE_QUANTILE))
    result["target_score_p75"] = target
    result["revenue_per_client_inr"] = REVENUE_PER_CLIENT_INR

    scen = scenarios(df, result["slope_pp_per_point"], target)

    df.to_csv(DATA_PROCESSED / "broker_panel.csv", index=False)
    scen.to_csv(DATA_PROCESSED / "scenarios.csv", index=False)
    with open(DATA_PROCESSED / "model_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))
    print(scen.to_string(index=False))


if __name__ == "__main__":
    main()
