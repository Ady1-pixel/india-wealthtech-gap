"""Interactive dashboard for the India WealthTech Experience Gap project.

Run:
    streamlit run app/streamlit_app.py
"""

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import TOPIC_LEXICONS  # noqa: E402

DATA = ROOT / "data" / "processed"
FINTECH = "#2a78d6"
INCUMBENT = "#eb6834"
CAT_COLORS = {"fintech": FINTECH, "incumbent": INCUMBENT}
CAT_LABELS = {"fintech": "Fintech-native", "incumbent": "Incumbent"}

st.set_page_config(page_title="India WealthTech Experience Gap", layout="wide")


@st.cache_data
def load():
    scores = pd.read_csv(DATA / "firm_scores.csv")
    panel = pd.read_csv(DATA / "broker_panel.csv")
    with open(DATA / "model_results.json") as f:
        model = json.load(f)
    return scores, panel, model


scores, panel, model = load()
scores["Category"] = scores["category"].map(CAT_LABELS)
panel["Category"] = panel["category"].map(CAT_LABELS)

st.title("The AI & UX gap in Indian investing")
st.caption(
    f"{scores['n_reviews_analyzed'].sum():,} Google Play reviews · 17 apps · "
    "NSE active-client data for 13 brokers · built from public data only"
)

tab1, tab2, tab3 = st.tabs(["Experience rankings", "Growth link", "What-if simulator"])

with tab1:
    c1, c2, c3 = st.columns(3)
    best = scores.nlargest(1, "experience_score").iloc[0]
    worst = scores.nsmallest(1, "experience_score").iloc[0]
    c1.metric("Best experience", best["firm"], f"{best['experience_score']:.0f} / 100")
    c2.metric("Weakest experience", worst["firm"], f"{worst['experience_score']:.0f} / 100")
    c3.metric(
        "Reviews mentioning AI features",
        f"{100 * (scores['ai_mention_rate'] * scores['n_reviews_analyzed']).sum() / scores['n_reviews_analyzed'].sum():.1f}%",
    )

    df = scores.sort_values("experience_score")
    fig = px.bar(
        df, x="experience_score", y="firm", orientation="h",
        color="Category", color_discrete_map={CAT_LABELS[k]: v for k, v in CAT_COLORS.items()},
        labels={"experience_score": "Digital Experience Score (0–100)", "firm": ""},
        text=df["experience_score"].round(0).astype(int),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=560, margin=dict(t=30, b=10), legend_title_text="",
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("What users complain about (share of 1–2★ reviews citing each theme)")
    theme_cols = [f"neg_{t}_rate" for t in TOPIC_LEXICONS]
    heat = scores.set_index("firm")[theme_cols] * 100
    heat.columns = [t.replace("neg_", "").replace("_rate", "").replace("_", " ") for t in theme_cols]
    fig2 = px.imshow(
        heat.round(1), color_continuous_scale="Blues", aspect="auto",
        labels=dict(color="% of reviews"),
    )
    fig2.update_layout(height=520, margin=dict(t=20))
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown(
        f"Cross-sectional fit across **{model['n_firms']} brokers**: each extra "
        f"experience point associates with **{model['slope_pp_per_point']:.2f} pp** "
        f"higher YoY client growth (95% bootstrap CI "
        f"{model['slope_ci_95'][0]:.2f} to {model['slope_ci_95'][1]:.2f}; "
        f"R² = {model['r_squared']:.2f}). Small sample, so read as directional "
        "evidence, not causation."
    )
    fig3 = px.scatter(
        panel, x="experience_score", y="growth_pct", text="firm",
        color="Category", color_discrete_map={CAT_LABELS[k]: v for k, v in CAT_COLORS.items()},
        labels={
            "experience_score": "Digital Experience Score (0–100)",
            "growth_pct": "Active-client growth, mid-2025 → June 2026 (%)",
        },
    )
    fig3.update_traces(textposition="top center", marker=dict(size=12))
    xs = [panel["experience_score"].min() - 1, panel["experience_score"].max() + 1]
    fig3.add_trace(
        go.Scatter(
            x=xs, y=[model["intercept"] + model["slope_pp_per_point"] * x for x in xs],
            mode="lines", line=dict(dash="dash", color="#52514e"), name="Fit",
        )
    )
    fig3.update_layout(height=560, margin=dict(t=30), legend_title_text="")
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown(
        "**What would happen if a firm closed its experience gap?** Pick a broker "
        "and a target score. The simulator applies the fitted elasticity "
        "(adjustable below, given the wide confidence band) to project extra "
        "client growth over one year."
    )
    brokers = panel.sort_values("firm")["firm"].tolist()
    c1, c2, c3 = st.columns(3)
    firm = c1.selectbox("Broker", brokers, index=brokers.index("ICICIdirect") if "ICICIdirect" in brokers else 0)
    row = panel.loc[panel["firm"] == firm].iloc[0]
    target = c2.slider("Target experience score", 60.0, 95.0, float(model["target_score_p75"]), 0.5)
    slope = c3.slider(
        "Elasticity (pp growth per score point)", 0.0, 1.0,
        round(model["slope_pp_per_point"], 2), 0.01,
    )
    rev_per_client = st.slider("Assumed annual revenue per active client (₹)", 1000, 8000, 3000, 250)

    gap = max(0.0, target - row["experience_score"])
    uplift_pp = slope * gap
    extra_clients = row["active_clients_2026"] * uplift_pp / 100
    extra_rev_cr = extra_clients * rev_per_client / 1e7

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current score", f"{row['experience_score']:.0f}")
    m2.metric("Score gap to close", f"{gap:.1f} pts")
    m3.metric("Projected extra clients (1 yr)", f"{extra_clients:,.0f}")
    m4.metric("Projected extra revenue", f"₹{extra_rev_cr:,.1f} cr")

    st.caption(
        f"Base: {row['active_clients_2026']:,.0f} active clients (June 2026). "
        "Illustrative scenario model, not a forecast: assumes the cross-sectional "
        "association is causal and linear, which the small sample cannot establish."
    )
