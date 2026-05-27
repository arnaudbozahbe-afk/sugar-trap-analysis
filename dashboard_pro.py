from __future__ import annotations

import re
import warnings
from collections import Counter

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sugar Trap — Blue Ocean Explorer",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .stApp { background: #0a0a0f; color: #f0ede8; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

  /* ── Hero ── */
  .hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a0a2e 50%, #0a1a1f 100%);
    border: 1px solid rgba(0,196,154,0.2);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(0,196,154,0.15) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero h1 { font-size: 2.8rem; font-weight: 800; color: #00C49A; margin: 0; line-height: 1.1; }
  .hero p  { color: #a0b0b8; font-size: 1.05rem; margin-top: 0.5rem; }

  /* ── KPI Cards ── */
  .metric-card {
    background: linear-gradient(145deg, #111827, #1f2937);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    transition: transform 0.2s;
  }
  .metric-card:hover { transform: translateY(-2px); }
  .metric-card .value { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#00C49A; }
  .metric-card .label { font-size:0.78rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; margin-top:4px; }

  /* ── Insight Box ── */
  .insight-box {
    background: linear-gradient(135deg, rgba(0,196,154,0.12), rgba(0,196,154,0.04));
    border-left: 4px solid #00C49A;
    border-radius: 0 12px 12px 0;
    padding: 1.4rem 1.8rem;
    margin: 1.5rem 0;
    font-size: 1.05rem;
    line-height: 1.7;
  }
  .insight-box strong { color: #00C49A; }

  /* ── Section labels ── */
  .section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: #00C49A;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.3rem;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #0d0d18 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
  }

  /* ── Tab overrides ── */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7280;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.05em;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(0,196,154,0.15) !important;
    color: #00C49A !important;
  }

  div[data-testid="stMetric"] { background: transparent; }
  .stSelectbox label, .stMultiSelect label { color: #9ca3af !important; font-size:0.82rem !important; }
  .stSlider label { color: #9ca3af !important; font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
COLS_WANTED = [
    "product_name", "brands", "categories_tags", "ingredients_text",
    "sugars_100g", "proteins_100g", "fat_100g",
    "fiber_100g", "energy_100g",
    "nutriscore_grade",
    "nutrition_grade_fr",
]

CATEGORY_RULES = [
    ("Protein Bars & Shakes", ["protein-bar","protein-shake","protein-powder","meal-replacement","sport","fitness"]),
    ("Nuts & Seeds",          ["nut","seed","almond","cashew","peanut","pistachio","walnut","sunflower-seed"]),
    ("Dairy & Eggs",          ["dairy","cheese","yogurt","yoghurt","milk","egg","butter","cream"]),
    ("Cereals & Granola",     ["cereal","granola","oat","muesli","breakfast"]),
    ("Chips & Savory Snacks", ["chip","crisp","popcorn","pretzel","cracker","savoury-snack","savory-snack","corn-snack"]),
    ("Candy & Confectionery", ["candy","chocolate","confectionery","sweet","gummy","marshmallow","caramel","lollipop"]),
    ("Baked Goods & Cookies", ["cookie","biscuit","cake","pastry","muffin","brownie","wafer"]),
    ("Fruit & Veg Snacks",    ["fruit-snack","dried-fruit","fruit-bar","vegetable-chip","raisin","date"]),
]

PROTEIN_KW = [
    "whey","casein","soy","pea protein","pea","hemp","peanut",
    "almond","cashew","egg","milk protein","chickpea","lentil",
    "quinoa","sunflower protein","rice protein","collagen",
]

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#c8d0d8",
    font_family="DM Sans",
    title_font_family="Syne",
    title_font_size=16,
    colorway=["#00C49A","#F59E0B","#EF4444","#818CF8","#FB923C","#34D399","#60A5FA","#E879F9"],
)

PRIMARY = "#00C49A"
ACCENT  = "#F59E0B"
DANGER  = "#EF4444"

# ── DATA PIPELINE ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_and_process(n_rows: int = 500_000):
    DATA_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"

    chunks = []
    try:
        reader = pd.read_csv(
            DATA_URL, sep="\t", nrows=n_rows,
            low_memory=False, chunksize=50_000, compression="infer",
            on_bad_lines="skip", encoding="utf-8",
        )
        for chunk in reader:
            keep = [c for c in COLS_WANTED if c in chunk.columns]
            chunks.append(chunk[keep])
        raw = pd.concat(chunks, ignore_index=True)
    except Exception:
        raw = pd.read_csv(
            "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv",
            sep="\t", nrows=n_rows, low_memory=False,
            on_bad_lines="skip", encoding="utf-8",
        )
        keep = [c for c in COLS_WANTED if c in raw.columns]
        raw = raw[keep]

    rows_loaded = len(raw)

    # Normalise nutriscore column
    if "nutrition_grade_fr" in raw.columns and "nutriscore_grade" not in raw.columns:
        raw = raw.rename(columns={"nutrition_grade_fr": "nutriscore_grade"})
    elif "nutriscore_grade" not in raw.columns:
        raw["nutriscore_grade"] = None

    # Clean
    df = raw.dropna(subset=["product_name","sugars_100g","proteins_100g"]).copy()
    df["product_name"] = df["product_name"].str.strip()
    df = df[df["product_name"] != ""]

    for col in ["sugars_100g","proteins_100g","fat_100g","fiber_100g","energy_100g"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["sugars_100g","proteins_100g","fat_100g","fiber_100g"]:
        df[col] = df[col].fillna(0)
        df = df[(df[col] >= 0) & (df[col] <= 100)]

    df = df[(df["energy_100g"] >= 0) & (df["energy_100g"] <= 4000)]
    macro = df["sugars_100g"] + df["proteins_100g"] + df["fat_100g"]
    df = df[macro <= 105]
    df.drop_duplicates(subset="product_name", inplace=True)

    rows_dropped_missing   = rows_loaded - len(raw.dropna(subset=["product_name","sugars_100g","proteins_100g"]))
    rows_final             = len(df)
    rows_dropped_outliers  = rows_loaded - rows_dropped_missing - rows_final
    retention              = rows_final / rows_loaded if rows_loaded else 0

    # Category
    def assign_cat(tags):
        if not isinstance(tags, str): return "Other"
        t = tags.lower()
        for name, kws in CATEGORY_RULES:
            if any(k in t for k in kws): return name
        return "Other"

    df["primary_category"] = df["categories_tags"].apply(assign_cat)

    # Quadrant / archetype
    sm = df["sugars_100g"].median()
    pm = df["proteins_100g"].median()

    def quadrant(r):
        hp = r["proteins_100g"] >= pm
        ls = r["sugars_100g"]   <= sm
        if hp and ls:   return " Healthy Power"
        elif hp:        return " High Protein / High Sugar"
        elif ls:        return " Low Protein / Low Sugar"
        else:           return " Saturated Zone"

    df["archetype"]    = df.apply(quadrant, axis=1)
    df["sugar_med"]    = sm
    df["protein_med"]  = pm

    # Nutriscore cleanup
    if "nutriscore_grade" in df.columns:
        df["nutriscore_grade"] = df["nutriscore_grade"].astype(str).str.upper()
        df.loc[~df["nutriscore_grade"].isin(["A","B","C","D","E"]), "nutriscore_grade"] = None
    else:
        df["nutriscore_grade"] = None

    cleaning_report = {
        "rows_loaded":           rows_loaded,
        "rows_final":            rows_final,
        "retention_rate":        retention,
        "dropped_missing_name":  rows_dropped_missing,
        "dropped_missing_nutrients": 0,
        "dropped_outliers":      rows_dropped_outliers,
        "dropped_duplicates":    0,
    }

    return df.reset_index(drop=True), cleaning_report


@st.cache_data
def score_opportunities(_df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    if weights is None:
        weights = {"health_gap": 0.40, "whitespace": 0.30, "market_size": 0.20, "fiber_gap": 0.10}

    global_sugar_med   = _df["sugars_100g"].median()
    global_protein_med = _df["proteins_100g"].median()
    global_fiber_med   = _df["fiber_100g"].median()

    rows = []
    for cat, grp in _df.groupby("primary_category"):
        if len(grp) < 20 or cat == "Other":
            continue
        med_s = grp["sugars_100g"].median()
        med_p = grp["proteins_100g"].median()
        med_f = grp["fiber_100g"].median()
        healthy_share = (grp["archetype"] == " Healthy Power").mean()
        rows.append({
            "primary_category": cat,
            "n_products":       len(grp),
            "median_sugar":     med_s,
            "median_protein":   med_p,
            "median_fiber":     med_f,
            "healthy_share":    healthy_share,
        })

    if not rows:
        return pd.DataFrame()

    sc = pd.DataFrame(rows)

    def norm(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)

    sc["_health_gap"]   = norm(sc["median_sugar"] - sc["median_protein"])
    sc["_whitespace"]   = norm(1 - sc["healthy_share"])
    sc["_market_size"]  = norm(sc["n_products"])
    sc["_fiber_gap"]    = norm(global_fiber_med - sc["median_fiber"])

    sc["opportunity_score"] = (
        weights["health_gap"]  * sc["_health_gap"]  +
        weights["whitespace"]  * sc["_whitespace"]   +
        weights["market_size"] * sc["_market_size"]  +
        weights["fiber_gap"]   * sc["_fiber_gap"]
    )

    return sc.drop(columns=[c for c in sc.columns if c.startswith("_")]).sort_values(
        "opportunity_score", ascending=False
    ).reset_index(drop=True)


def recommend_target(df: pd.DataFrame, category: str) -> dict:
    grp = df[df["primary_category"] == category]
    sugar_10  = grp["sugars_100g"].quantile(0.10)
    prot_90   = grp["proteins_100g"].quantile(0.90)
    fiber_90  = grp["fiber_100g"].quantile(0.90) if grp["fiber_100g"].median() > 1 else None
    return {
        "category":                category,
        "n_competitors":           len(grp),
        "category_median_sugar_g": round(grp["sugars_100g"].median(), 1),
        "category_median_protein_g": round(grp["proteins_100g"].median(), 1),
        "target_sugar_g":          round(sugar_10, 1),
        "target_protein_g":        round(prot_90, 1),
        "target_fiber_g":          round(fiber_90, 1) if fiber_90 else None,
    }


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-label">Dataset</p>', unsafe_allow_html=True)
    n_rows = st.selectbox(
        "Rows to load", [100_000, 250_000, 500_000], index=2,
        format_func=lambda x: f"{x:,}",
    )

    st.markdown("---")
    st.markdown('<p class="section-label">Filters</p>', unsafe_allow_html=True)

    with st.spinner("Loading Open Food Facts…"):
        df, cleaning_report = load_and_process(n_rows)

    all_cats = sorted([c for c in df["primary_category"].unique() if c != "Other"])
    sel_cats = st.multiselect("Categories", all_cats, default=all_cats)

    sugar_range  = st.slider("Sugar range (g / 100g)",   0.0, 100.0, (0.0, 100.0), 1.0)
    prot_range   = st.slider("Protein range (g / 100g)", 0.0,  50.0, (0.0,  50.0), 1.0)

    st.markdown("---")
    st.markdown('<p class="section-label">Cleaning Audit</p>', unsafe_allow_html=True)
    st.metric("Rows loaded",   f"{cleaning_report['rows_loaded']:,}")
    st.metric("Rows retained", f"{cleaning_report['rows_final']:,}",
              f"{cleaning_report['retention_rate']:.1%}")
    with st.expander("Drop breakdown"):
        for k in ("dropped_missing_name", "dropped_missing_nutrients",
                  "dropped_outliers", "dropped_duplicates"):
            st.text(f"{k.replace('dropped_','').replace('_',' ').title()}: "
                    f"{cleaning_report[k]:,}")

    st.markdown(
        '<p style="color:#374151;font-size:0.75rem;margin-top:1rem;">Open Food Facts · CC0 License</p>',
        unsafe_allow_html=True,
    )

# ── FILTER ─────────────────────────────────────────────────────────────────────
mask = (
    df["primary_category"].isin(sel_cats)
    & df["sugars_100g"].between(*sugar_range)
    & df["proteins_100g"].between(*prot_range)
)
fdf  = df[mask]
blue = fdf[fdf["archetype"] == " Healthy Power"]
bo_pct = len(blue) / len(fdf) * 100 if len(fdf) else 0

scores = score_opportunities(fdf)

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="section-label">Helix CPG Partners · Strategic Market Intelligence</div>
  <h1> Sugar Trap</h1>
  <p>Blue Ocean Gap Analysis · Open Food Facts Dataset · 2024</p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
sm = fdf["sugar_med"].iloc[0]  if len(fdf) else 0
pm = fdf["protein_med"].iloc[0] if len(fdf) else 0
top_score = scores.iloc[0]["opportunity_score"] if not scores.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (f"{len(fdf):,}",                      "Products Analysed"),
    (f"{len(fdf['primary_category'].unique())}","Categories"),
    (f"{bo_pct:.1f}%",                     "Blue Ocean Share"),
    (f"{pm:.1f}g",                          "Median Protein"),
    (f"{top_score:.2f}",                    "Top Opp. Score"),
]
for col, (val, lbl) in zip([k1,k2,k3,k4,k5], kpis):
    col.markdown(
        f'<div class="metric-card">'
        f'<div class="value">{val}</div>'
        f'<div class="label">{lbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab_overview, tab_matrix, tab_opportunity, tab_ingredients, tab_data = st.tabs([
    "🎯 Overview",
    "📈 Nutrient Matrix",
    "🌊 Opportunity Engine",
    "🌱 Hidden Gems",
    "🔍 Data Explorer",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    if scores.empty:
        st.warning("No categories meet the minimum sample size after filtering.")
    else:
        top = scores.iloc[0]
        rec = recommend_target(fdf, top["primary_category"])

        st.markdown(
            f"""
            <div class="insight-box">
               <b>Key Insight</b><br>
              Based on the data, the biggest market opportunity is in
              <strong>{rec['category']}</strong> —
              <strong>{rec['n_competitors']:,} competing products</strong> whose median product carries
              <strong>{rec['category_median_sugar_g']}g of sugar</strong> and only
              <strong>{rec['category_median_protein_g']}g of protein</strong> per 100g.<br><br>
              We recommend launching with
              <strong>≥ {rec['target_protein_g']}g of protein</strong> and
              <strong>≤ {rec['target_sugar_g']}g of sugar</strong>
              {f"and <strong>≥ {rec['target_fiber_g']}g of fiber</strong>" if rec['target_fiber_g'] else ''}
              per 100g — placing the product in the top decile of healthiness for this category.
              The Blue Ocean quadrant represents only <strong>{bo_pct:.1f}%</strong> of the market — a clear
              white space with room for disruption.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Opportunity ranking bar chart
        st.markdown('<p class="section-label">Opportunity Ranking by Category</p>', unsafe_allow_html=True)
        fig_rank = px.bar(
            scores, x="opportunity_score", y="primary_category",
            orientation="h",
            color="opportunity_score",
            color_continuous_scale=[[0, "#1e3a5f"], [1, PRIMARY]],
            hover_data={"n_products": True, "median_sugar": ":.1f",
                        "median_protein": ":.1f", "healthy_share": ":.1%"},
            labels={"opportunity_score": "Opportunity Score (0 – 1)", "primary_category": ""},
        )
        fig_rank.update_layout(
            **PLOTLY_THEME,
            height=400,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_rank, use_container_width=True)

        # Category breakdown mini-bar
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<p class="section-label">Category Breakdown</p>', unsafe_allow_html=True)
            cat_cnt = fdf["primary_category"].value_counts().reset_index()
            cat_cnt.columns = ["Category", "Count"]
            fig_cat = px.bar(
                cat_cnt, x="Count", y="Category", orientation="h",
                color="Count", color_continuous_scale=["#1e3a5f", PRIMARY],
                height=320,
            )
            fig_cat.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                                   yaxis=dict(autorange="reversed"),
                                   margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_cat, use_container_width=True)

        with c2:
            st.markdown('<p class="section-label">Market Quadrant Split</p>', unsafe_allow_html=True)
            quad_cnt = fdf["archetype"].value_counts().reset_index()
            quad_cnt.columns = ["Quadrant", "Count"]
            fig_donut = go.Figure(go.Pie(
                labels=quad_cnt["Quadrant"], values=quad_cnt["Count"],
                hole=0.6,
                marker_colors=[PRIMARY, ACCENT, "#64748B", DANGER],
                textinfo="percent",
                hovertemplate="%{label}<br>%{value:,} products<extra></extra>",
            ))
            fig_donut.update_layout(
                **PLOTLY_THEME, height=320,
                legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#9ca3af"),
                annotations=[dict(text="Market<br>Split", x=0.5, y=0.5,
                                  font=dict(size=14, color="#c8d0d8", family="Syne"),
                                  showarrow=False)],
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NUTRIENT MATRIX
# ═══════════════════════════════════════════════════════════════════════════════
with tab_matrix:
    st.markdown('<p class="section-label">Story 3 · The Sugar × Protein Matrix</p>', unsafe_allow_html=True)
    st.caption(
        "Each dot is a product. The **top-left quadrant** (low sugar, high protein) "
        "is the 'Healthy Power' zone — where consumer demand exists but supply doesn't."
    )

    sample = fdf.sample(min(12_000, len(fdf)), random_state=42)
    color_map = {
        " Healthy Power":             PRIMARY,
        " High Protein / High Sugar": ACCENT,
        " Low Protein / Low Sugar":   "#64748B",
        " Saturated Zone":            DANGER,
    }
    fig_scatter = px.scatter(
        sample, x="sugars_100g", y="proteins_100g",
        color="archetype",
        color_discrete_map=color_map,
        symbol="primary_category",
        hover_data={"product_name": True, "brands": True,
                    "fiber_100g": ":.1f", "primary_category": True},
        opacity=0.5, height=480,
        labels={"sugars_100g": "Sugar (g / 100g)", "proteins_100g": "Protein (g / 100g)"},
    )
    fig_scatter.add_vline(x=sm, line_dash="dot", line_color="rgba(255,255,255,0.25)",
                          annotation_text=f"Median sugar {sm:.1f}g",
                          annotation_font_color="#6b7280")
    fig_scatter.add_hline(y=pm, line_dash="dot", line_color="rgba(255,255,255,0.25)",
                          annotation_text=f"Median protein {pm:.1f}g",
                          annotation_font_color="#6b7280",
                          annotation_position="bottom right")
    # Shade the Blue Ocean quadrant
    fig_scatter.add_shape(
        type="rect", x0=0, x1=sm, y0=pm, y1=sample["proteins_100g"].max(),
        fillcolor=PRIMARY, opacity=0.06, line_width=0,
    )
    fig_scatter.add_annotation(
        x=sm * 0.4, y=sample["proteins_100g"].max() * 0.92,
        text="<b>HEALTHY POWER<br>Blue Ocean</b>",
        showarrow=False, font=dict(size=13, color=PRIMARY),
    )
    fig_scatter.update_traces(marker_size=4)
    fig_scatter.update_layout(
        **PLOTLY_THEME,
        legend=dict(orientation="h", y=-0.18, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Quadrant population (filtered view)**")
        quad_df = fdf["archetype"].value_counts().reset_index()
        quad_df.columns = ["Archetype", "Count"]
        st.dataframe(quad_df, hide_index=True, use_container_width=True)
    with c2:
        st.markdown("**Nutri-Score × Protein Matrix**")
        scored = fdf.dropna(subset=["nutriscore_grade"])
        if len(scored) > 100:
            heat = (
                scored.groupby(["primary_category","nutriscore_grade"])
                ["proteins_100g"].mean().round(1).reset_index()
            )
            pivot = heat.pivot(index="primary_category",
                               columns="nutriscore_grade",
                               values="proteins_100g").fillna(0)
            grade_cols = [g for g in ["A","B","C","D","E"] if g in pivot.columns]
            pivot = pivot[grade_cols]
            fig_heat = go.Figure(go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale=[[0,"#1a0a2e"],[0.5, ACCENT],[1, PRIMARY]],
                text=pivot.values.round(1),
                texttemplate="%{text}g",
                hoverongaps=False,
                showscale=True,
                colorbar=dict(title="Protein (g)", tickfont_color="#9ca3af"),
            ))
            fig_heat.update_layout(
                **PLOTLY_THEME, height=320,
                xaxis_title="Nutri-Score", yaxis_title="",
                xaxis=dict(tickfont_color="#9ca3af"),
                yaxis=dict(tickfont_color="#9ca3af"),
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption("Cross-referencing Nutri-Score with protein reveals *investable* white space — products both nutritionally superior AND carrying a label that drives EU/UK purchase intent.")
        else:
            st.info("Not enough Nutri-Score data in current filter selection.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — OPPORTUNITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_opportunity:
    st.markdown('<p class="section-label">Story 4 · Blue Ocean Category Ranking</p>', unsafe_allow_html=True)
    if len(blue) > 0:
        bo_cats = (
            blue.groupby("primary_category")
            .agg(
                products=("product_name","count"),
                avg_protein=("proteins_100g","mean"),
                avg_sugar=("sugars_100g","mean"),
            )
            .round(1).reset_index()
            .sort_values("avg_protein", ascending=False)
        )
        fig_bo = px.bar(
            bo_cats, x="primary_category", y="avg_protein",
            color="avg_sugar", color_continuous_scale="RdYlGn_r",
            text="products", height=380,
            labels={"primary_category":"","avg_protein":"Avg Protein (g)","avg_sugar":"Avg Sugar (g)"},
        )
        fig_bo.update_traces(texttemplate="%{text} products", textposition="outside")
        fig_bo.update_layout(**PLOTLY_THEME, xaxis_tickangle=-30,
                              coloraxis_colorbar_title="Sugar",
                              margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_bo, use_container_width=True)

    st.markdown("---")
    st.subheader("Stress-test the opportunity weights")
    st.caption("Each score combines four normalised signals. Adjust the sliders to explore how the ranking shifts.")

    c1, c2, c3, c4 = st.columns(4)
    w_health = c1.slider("Health gap",   0.0, 1.0, 0.40, 0.05)
    w_white  = c2.slider("Whitespace",   0.0, 1.0, 0.30, 0.05)
    w_market = c3.slider("Market size",  0.0, 1.0, 0.20, 0.05)
    w_fiber  = c4.slider("Fiber gap",    0.0, 1.0, 0.10, 0.05)

    total = w_health + w_white + w_market + w_fiber
    if total > 0:
        custom_weights = {
            "health_gap":  w_health / total,
            "whitespace":  w_white  / total,
            "market_size": w_market / total,
            "fiber_gap":   w_fiber  / total,
        }
        custom_scores = score_opportunities(fdf, weights=custom_weights)
        st.dataframe(
            custom_scores[[
                "primary_category","n_products","median_sugar",
                "median_protein","median_fiber","healthy_share","opportunity_score",
            ]].round(3),
            hide_index=True, use_container_width=True,
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — HIDDEN GEMS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ingredients:
    st.markdown('<p class="section-label">Bonus · Top Protein Sources — Healthy Power Products</p>', unsafe_allow_html=True)
    st.caption(
        "We mined the ingredients lists of every product in the **Healthy Power** cluster "
        "(low sugar + high protein) to surface the protein sources you should consider for the R&D brief."
    )

    st.metric("Products in Healthy Power cluster", f"{len(blue):,}")

    blue_ingr = blue.dropna(subset=["ingredients_text"])
    if len(blue_ingr) > 0:
        all_src = []
        for txt in blue_ingr["ingredients_text"]:
            t = txt.lower()
            all_src.extend([k for k in PROTEIN_KW if k in t])

        top10 = Counter(all_src).most_common(12)
        if top10:
            src_df = pd.DataFrame(top10, columns=["Ingredient","Frequency"])
            fig_src = px.bar(
                src_df, x="Frequency", y="Ingredient",
                orientation="h", color="Frequency",
                color_continuous_scale=["#0f3460", PRIMARY],
                height=420,
                labels={"Ingredient":"","Frequency":"# Products"},
            )
            fig_src.update_layout(
                **PLOTLY_THEME, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig_src, use_container_width=True)

            st.markdown("** Top 3 protein sources to consider for the new product:**")
            for i, (ingredient, freq) in enumerate(top10[:3]):
                share = freq / len(blue_ingr)
                st.markdown(f"{i+1}. **{ingredient.title()}** — found in {share:.0%} of Healthy Power products ({freq:,} mentions)")
    else:
        st.info("No ingredient data available in the current filtered selection.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown('<p class="section-label">Browse the Cleaned Dataset</p>', unsafe_allow_html=True)
    st.caption("Search and filter the underlying product-level data.")

    col_search, col_quadrant = st.columns([3, 1])
    with col_search:
        search = st.text_input("Search by product name or brand", "")
    with col_quadrant:
        quad_filter = st.selectbox("Quadrant", ["All"] + list(fdf["archetype"].unique()))

    explorer = fdf.copy()
    if search:
        s = search.lower()
        explorer = explorer[
            explorer["product_name"].str.lower().str.contains(s, na=False)
            | explorer["brands"].str.lower().str.contains(s, na=False)
        ]
    if quad_filter != "All":
        explorer = explorer[explorer["archetype"] == quad_filter]

    # Blue Ocean only tab
    with st.expander(" Explore Blue Ocean Products Only", expanded=False):
        cols_bo = ["product_name","primary_category","proteins_100g","sugars_100g",
                   "fat_100g","fiber_100g","nutriscore_grade"]
        st.dataframe(
            blue[[c for c in cols_bo if c in blue.columns]]
            .sort_values("proteins_100g", ascending=False).reset_index(drop=True),
            use_container_width=True, height=280,
        )

    cols_show = ["product_name","brands","primary_category","archetype",
                 "sugars_100g","proteins_100g","fiber_100g","energy_100g","nutriscore_grade"]
    st.dataframe(
        explorer[[c for c in cols_show if c in explorer.columns]].head(500),
        hide_index=True, use_container_width=True,
    )
    st.caption(f"Showing first 500 of {len(explorer):,} matching rows.")

    csv = explorer.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download filtered data as CSV",
        csv, "sugar_trap_filtered.csv", "text/csv",
    )

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;color:#374151;font-size:0.75rem;padding:1.5rem 0 1rem'>
  Sugar Trap Analysis · Helix CPG Partners ·
  Data: <a href='https://world.openfoodfacts.org/data' style='color:#00C49A;'>Open Food Facts</a> (CC0)
</div>
""", unsafe_allow_html=True)
