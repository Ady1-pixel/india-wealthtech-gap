"""Interactive dashboard for the India WealthTech Experience Gap project.

Styled as a sector research note: serif masthead, monospace data,
coverage-universe ladder with analyst-style ratings.

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

# ---- tokens ----------------------------------------------------------------
BG = "#12151c"
SURFACE = "#1a1e27"
LINE = "#2a3040"
INK = "#f4f2ec"
INK2 = "#a8adba"
FINTECH = "#3987e5"
INCUMBENT = "#d95926"
MARIGOLD = "#eda100"
CAT_COLORS = {"fintech": FINTECH, "incumbent": INCUMBENT}
CAT_LABELS = {"fintech": "Fintech-native", "incumbent": "Incumbent"}

st.set_page_config(
    page_title="India WealthTech: The Experience Gap",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Archivo', sans-serif; }
.stApp { background: #12151c; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 2.2rem; max-width: 1150px; }

/* masthead */
.note-eyebrow {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.18em;
  color: #eda100; text-transform: uppercase; display: flex; justify-content: space-between;
  border-bottom: 1px solid #2a3040; padding-bottom: 0.55rem; margin-bottom: 1.4rem;
}
.note-eyebrow span:last-child { color: #a8adba; }
h1.note-title, .stApp h1.note-title {
  font-family: 'Fraunces', serif !important; font-weight: 600 !important; font-size: 3.4rem;
  line-height: 1.04; color: #f4f2ec; margin: 0 0 0.6rem 0; letter-spacing: -0.01em; padding: 0;
}
.note-title em { font-style: italic; color: #eda100; }
.note-sub { font-size: 1.05rem; color: #a8adba; max-width: 46rem; margin-bottom: 1.1rem; }
.dateline {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.74rem; color: #a8adba;
  display: flex; gap: 1.6rem; flex-wrap: wrap; border-top: 1px solid #2a3040;
  border-bottom: 1px solid #2a3040; padding: 0.5rem 0; margin-bottom: 0.4rem;
}
.dateline b { color: #f4f2ec; font-weight: 500; }

/* tabs as research-note sections */
.stTabs [data-baseweb="tab-list"] { gap: 1.8rem; border-bottom: 1px solid #2a3040; }
.stTabs [data-baseweb="tab"] {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: #a8adba; background: transparent; padding: 0.6rem 0;
}
.stTabs [aria-selected="true"] { color: #f4f2ec; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #eda100; height: 2px; }
.stTabs [data-baseweb="tab-border"] { background: transparent; }

/* stat tiles */
.tile-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 1.2rem 0 1.6rem 0; }
.tile { background: #1a1e27; border: 1px solid #2a3040; border-radius: 6px; padding: 1rem 1.1rem; }
.tile .k { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: #a8adba; margin-bottom: 0.45rem; }
.tile .v { font-family: 'Fraunces', serif; font-weight: 600; font-size: 2.1rem; color: #f4f2ec; line-height: 1; }
.tile .d { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #a8adba; margin-top: 0.4rem; }
.tile.accent { border-color: #eda100; }
.tile.accent .v { color: #eda100; }

/* coverage ladder */
.ladder { border: 1px solid #2a3040; border-radius: 6px; overflow: hidden; margin-bottom: 1.4rem; }
.ladder-head, .lrow {
  display: grid; grid-template-columns: 2.4rem 15rem 3.2rem 1fr 7rem 6.4rem;
  gap: 0.9rem; align-items: center; padding: 0.42rem 0.9rem;
}
.ladder-head {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: #a8adba; background: #1a1e27; border-bottom: 1px solid #2a3040;
}
.lrow { border-bottom: 1px solid #1e232e; }
.lrow:last-child { border-bottom: none; }
.lrow .rank { font-family: 'IBM Plex Mono', monospace; font-size: 0.74rem; color: #a8adba; }
.lrow .firm { font-size: 0.92rem; color: #f4f2ec; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lrow .firm small { display: block; font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
  letter-spacing: 0.1em; text-transform: uppercase; color: #a8adba; }
.lrow .score { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: #f4f2ec; text-align: right; }
.bar-track { background: #1e232e; border-radius: 3px; height: 10px; position: relative; }
.bar-fill { height: 100%; border-radius: 3px; }
.lrow .clients { font-family: 'IBM Plex Mono', monospace; font-size: 0.74rem; color: #a8adba; text-align: right; }
.chip { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em;
  padding: 0.18rem 0.5rem; border-radius: 3px; border: 1px solid #2a3040; color: #a8adba;
  text-align: center; text-transform: uppercase; }
.chip.leader { border-color: #eda100; color: #eda100; }
.chip.laggard { border-color: #d95926; color: #d95926; }

.legend-row { display: flex; gap: 1.4rem; margin: 0.2rem 0 0.7rem 0;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #a8adba; }
.legend-row i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 0.4rem; }

.thesis { border-left: 2px solid #eda100; padding: 0.2rem 0 0.2rem 1rem; margin: 1.1rem 0 1.2rem 0;
  font-family: 'Fraunces', serif; font-size: 1.25rem; color: #f4f2ec; max-width: 46rem; }
.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: #a8adba; margin: 1.6rem 0 0.5rem 0; }

/* scenario result card */
.result-card { background: #1a1e27; border: 1px solid #eda100; border-radius: 6px; padding: 1.4rem 1.6rem; }
.result-card .headline { font-family: 'Fraunces', serif; font-weight: 600; font-size: 2.6rem; color: #f4f2ec; line-height: 1.1; }
.result-card .headline span { color: #eda100; }
.result-card .sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.76rem; color: #a8adba; margin-top: 0.7rem; line-height: 1.7; }

.src-foot { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: #a8adba;
  border-top: 1px solid #2a3040; padding-top: 0.7rem; margin-top: 2.2rem; }

/* ---- motion: content arrives, quietly ---- */
@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
.note-eyebrow { animation: rise 0.4s cubic-bezier(0.22, 1, 0.36, 1) both; }
h1.note-title, .stApp h1.note-title { animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.05s both; }
.note-sub { animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.12s both; }
.dateline { animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.18s both; }
.tile { animation: rise 0.45s cubic-bezier(0.22, 1, 0.36, 1) both; }
.tile-row .tile:nth-child(2) { animation-delay: 0.07s; }
.tile-row .tile:nth-child(3) { animation-delay: 0.14s; }
.lrow { animation: rise 0.4s cubic-bezier(0.22, 1, 0.36, 1) both; }
.bar-fill { transform-origin: left; animation: grow 0.6s cubic-bezier(0.22, 1, 0.36, 1) both; }
.thesis, .ladder, .result-card { animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both; }

/* ---- interaction states ---- */
.tile, .lrow, .chip { transition: background 0.18s ease-out, border-color 0.18s ease-out; }
.tile:hover { border-color: #3a4155; }
.tile.accent:hover { border-color: #f7b733; }
.lrow:hover { background: #1e232e; }
.stTabs [data-baseweb="tab"] { transition: color 0.18s ease-out; }
.stTabs [data-baseweb="tab"]:hover { color: #f4f2ec; }
.stTabs [data-baseweb="tab"]:focus-visible { outline: 2px solid #eda100; outline-offset: 3px; }

/* ---- responsive ---- */
@media (max-width: 900px) {
  h1.note-title, .stApp h1.note-title { font-size: 2.2rem; }
  .tile-row { grid-template-columns: 1fr; }
  .ladder-head, .lrow { grid-template-columns: 2rem 1fr 2.6rem 5rem; gap: 0.5rem; }
  .ladder-head div:nth-child(4), .ladder-head div:nth-child(5),
  .lrow .bar-track, .lrow .clients { display: none; }
  .dateline { gap: 0.9rem; }
}

/* ---- accessibility: respect reduced motion ---- */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---- helpers ---------------------------------------------------------------
def fmt_inr(n: float) -> str:
    """Indian digit grouping: 13053752 -> 1,30,53,752."""
    s = str(int(round(n)))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def rating(score: float) -> tuple[str, str]:
    if score >= 84:
        return "Leader", "leader"
    if score >= 75:
        return "In line", ""
    return "Laggard", "laggard"


def style_fig(fig, height=520):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=12, color=INK2),
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(title_text="", font=dict(color=INK2)),
        xaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
        yaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
    )
    return fig


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
n_reviews = int(scores["n_reviews_analyzed"].sum())
ai_pct = 100 * (scores["ai_mention_rate"] * scores["n_reviews_analyzed"]).sum() / n_reviews

# ---- masthead --------------------------------------------------------------
st.markdown(
    f"""
<div class="note-eyebrow"><span>India WealthTech · Sector Note</span><span>July 2026</span></div>
<h1 class="note-title">The <em>experience gap</em> in Indian investing</h1>
<div class="note-sub">What would happen if India's investment firms fixed their apps?
{n_reviews:,} Play Store reviews, scored and tied to NSE client growth, put a number on it.</div>
<div class="dateline">
  <span>REVIEWS <b>{n_reviews:,}</b></span>
  <span>APPS <b>17</b></span>
  <span>BROKERS IN GROWTH MODEL <b>{model["n_firms"]}</b></span>
  <span>DATA <b>Google Play · NSE</b></span>
</div>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["Coverage", "Growth link", "Scenario desk"])

# ---- tab 1: coverage -------------------------------------------------------
with tab1:
    best = scores.nlargest(1, "experience_score").iloc[0]
    worst = scores.nsmallest(1, "experience_score").iloc[0]
    st.markdown(
        f"""
<div class="tile-row">
  <div class="tile"><div class="k">Best experience</div>
    <div class="v">{best['experience_score']:.0f}</div>
    <div class="d">{best['firm']} · fintech-native</div></div>
  <div class="tile"><div class="k">Weakest experience</div>
    <div class="v">{worst['experience_score']:.0f}</div>
    <div class="d">{worst['firm']} · incumbent</div></div>
  <div class="tile accent"><div class="k">Reviews mentioning AI</div>
    <div class="v">{ai_pct:.1f}%</div>
    <div class="d">the whitespace nobody owns yet</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Coverage universe · Digital Experience Score</div>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="legend-row">
        <span><i style="background:{FINTECH}"></i>Fintech-native</span>
        <span><i style="background:{INCUMBENT}"></i>Incumbent</span></div>""",
        unsafe_allow_html=True,
    )

    clients_map = dict(zip(panel["firm"], panel["active_clients_2026"]))
    rows = []
    ranked = scores.sort_values("experience_score", ascending=False).reset_index(drop=True)
    lo, hi = 60, 92  # bar scale bounds chosen for resolution across the observed range
    for i, r in ranked.iterrows():
        label, cls = rating(r["experience_score"])
        width = 100 * (r["experience_score"] - lo) / (hi - lo)
        clients = clients_map.get(r["firm"])
        clients_txt = fmt_inr(clients) if clients is not None and pd.notna(clients) else "·"
        delay = 0.05 + i * 0.035
        rows.append(
            f"""<div class="lrow" style="animation-delay:{delay:.3f}s">
  <div class="rank">{i + 1:02d}</div>
  <div class="firm">{r['firm']}<small>{CAT_LABELS[r['category']]}</small></div>
  <div class="score">{r['experience_score']:.0f}</div>
  <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:{CAT_COLORS[r['category']]};animation-delay:{delay + 0.1:.3f}s"></div></div>
  <div class="clients">{clients_txt}</div>
  <div class="chip {cls}">{label}</div>
</div>"""
        )
    st.markdown(
        """<div class="ladder">
<div class="ladder-head"><div>#</div><div>Firm</div><div style="text-align:right">Score</div>
<div>Scale 60–92</div><div style="text-align:right">NSE clients</div><div style="text-align:center">Rating</div></div>"""
        + "".join(rows)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Complaint anatomy · share of 1–2★ reviews citing each theme</div>', unsafe_allow_html=True)
    theme_cols = [f"neg_{t}_rate" for t in TOPIC_LEXICONS]
    heat = ranked.set_index("firm")[theme_cols] * 100
    heat.columns = [t.replace("neg_", "").replace("_rate", "").replace("_", " ") for t in theme_cols]
    fig2 = px.imshow(
        heat.round(1),
        color_continuous_scale=[[0, SURFACE], [1, FINTECH]],
        aspect="auto",
        labels=dict(color="% of reviews"),
    )
    fig2.update_coloraxes(colorbar=dict(tickfont=dict(color=INK2)))
    st.plotly_chart(style_fig(fig2, 520), use_container_width=True)

# ---- tab 2: growth link ----------------------------------------------------
with tab2:
    st.markdown(
        '<div class="thesis">No broker in the bottom half of the experience table grew its client base this year.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"Cross-sectional fit across **{model['n_firms']} brokers**: each extra experience point "
        f"associates with **{model['slope_pp_per_point']:.2f} pp** higher YoY client growth "
        f"(95% bootstrap CI {model['slope_ci_95'][0]:.2f} to {model['slope_ci_95'][1]:.2f}; "
        f"R² = {model['r_squared']:.2f}). Small sample, so read as directional evidence, not causation."
    )
    fig3 = px.scatter(
        panel, x="experience_score", y="growth_pct", text="firm",
        color="Category",
        color_discrete_map={CAT_LABELS[k]: v for k, v in CAT_COLORS.items()},
        labels={
            "experience_score": "Digital Experience Score (0–100)",
            "growth_pct": "Active-client growth, mid-2025 → June 2026 (%)",
        },
    )
    fig3.update_traces(textposition="top center", marker=dict(size=11), textfont=dict(size=10, color=INK2))
    xs = [panel["experience_score"].min() - 1, panel["experience_score"].max() + 1]
    fig3.add_trace(
        go.Scatter(
            x=xs, y=[model["intercept"] + model["slope_pp_per_point"] * x for x in xs],
            mode="lines", line=dict(dash="dash", color=INK2, width=1.5), name="Fit",
        )
    )
    fig3.add_hline(y=0, line_color=LINE, line_width=1)
    st.plotly_chart(style_fig(fig3, 560), use_container_width=True)

# ---- tab 3: scenario desk --------------------------------------------------
with tab3:
    st.markdown(
        '<div class="thesis">Pick a broker. Close its gap. Read off what the upgrade is worth.</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([5, 7], gap="large")
    with left:
        brokers = panel.sort_values("firm")["firm"].tolist()
        firm = st.selectbox("Broker", brokers, index=brokers.index("ICICIdirect") if "ICICIdirect" in brokers else 0)
        row = panel.loc[panel["firm"] == firm].iloc[0]
        target = st.slider("Target experience score", 60.0, 95.0, float(model["target_score_p75"]), 0.5)
        slope = st.slider(
            "Elasticity (pp growth per score point)", 0.0, 1.0,
            round(model["slope_pp_per_point"], 2), 0.01,
            help="Fitted value shown as default; the CI is wide, so treat as an assumption dial.",
        )
        rev_per_client = st.slider("Assumed annual revenue per active client (₹)", 1000, 8000, 3000, 250)

    gap = max(0.0, target - row["experience_score"])
    uplift_pp = slope * gap
    extra_clients = row["active_clients_2026"] * uplift_pp / 100
    extra_rev_cr = extra_clients * rev_per_client / 1e7

    with right:
        st.markdown(
            f"""
<div class="result-card">
  <div class="headline">+{fmt_inr(extra_clients)} clients<br/><span>₹{extra_rev_cr:,.1f} cr</span> a year</div>
  <div class="sub">{firm.upper()} · score {row['experience_score']:.0f} → {target:.0f}
  ({gap:.1f} pts) · uplift {uplift_pp:.2f} pp on {fmt_inr(row['active_clients_2026'])} active clients ·
  ₹{rev_per_client:,}/client/yr<br/><br/>
  Illustrative scenario, not a forecast: assumes the cross-sectional association
  is causal and linear, which n={model['n_firms']} cannot establish.</div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="src-foot">SOURCES · Google Play (via google-play-scraper, IN storefront) · '
    "NSE active clients via Chittorgarh monthly top-20 rankings & StartupTalky Jun-2026 analysis · "
    "Analysis & code: github.com/Ady1-pixel/india-wealthtech-gap</div>",
    unsafe_allow_html=True,
)
