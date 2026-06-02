import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy — Shipping Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f0f1a; }
    section[data-testid="stSidebar"] { background-color: #16162a; }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e35 0%, #252540 100%);
        border: 1px solid #2e2e50;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }
    .metric-title { color: #8888bb; font-size: 13px; font-weight: 600;
                    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
    .metric-value { color: #ffffff; font-size: 32px; font-weight: 700; line-height: 1.1; }
    .metric-sub   { color: #5555aa; font-size: 12px; margin-top: 4px; }

    /* Section headers */
    .section-header {
        color: #ccccff;
        font-size: 20px;
        font-weight: 700;
        margin: 8px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2e2e50;
    }
    .page-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .page-sub { color: #8888bb; font-size: 14px; margin-bottom: 20px; }

    /* Chips */
    .chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .chip-good  { background:#1a3a2a; color:#4ade80; border:1px solid #2a6a4a; }
    .chip-warn  { background:#3a3a1a; color:#facc15; border:1px solid #6a5a1a; }
    .chip-bad   { background:#3a1a1a; color:#f87171; border:1px solid #6a2a2a; }

    /* Streamlit overrides */
    div[data-testid="stMetric"] { background: #1e1e35; border-radius:12px; padding:12px; }
    div[data-testid="stMetricValue"] > div { color: #ffffff !important; }
    div[data-testid="stMetricLabel"] > div { color: #8888bb !important; }
    .stSlider > div { color: #ccccff; }
    h1, h2, h3 { color: #ccccff !important; }
    p, li { color: #aaaacc; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING & PREP
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"U:\unified mentorship\project 2\Nassau Candy Distributor.csv")
    # Parse dates  (dd-mm-yyyy format)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True, errors="coerce")
    df["Lead Time"]  = (df["Ship Date"] - df["Order Date"]).dt.days
    df = df[df["Lead Time"] >= 0]
    # Route label: Region → State
    df["Route"] = df["Region"] + " → " + df["State/Province"]
    return df

df_full = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍬 Nassau Candy")
    st.markdown("**Shipping Intelligence**")
    st.markdown("---")

    st.markdown("#### 📅 Date Range")
    min_date = df_full["Order Date"].min().date()
    max_date = df_full["Order Date"].max().date()
    date_range = st.date_input(
        "Order dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

    st.markdown("#### 🗺️ Region")
    all_regions = sorted(df_full["Region"].dropna().unique())
    sel_regions = st.multiselect("Select regions", all_regions, default=all_regions,
                                  label_visibility="collapsed")

    st.markdown("#### 🚚 Ship Mode")
    all_modes = sorted(df_full["Ship Mode"].dropna().unique())
    sel_modes = st.multiselect("Select ship modes", all_modes, default=all_modes,
                                label_visibility="collapsed")

    st.markdown("#### ⏱️ Delay Threshold (days)")
    threshold = st.slider("Flag orders slower than:", 1, 30, 7, 1,
                           label_visibility="collapsed")

    st.markdown("#### 🍫 Division")
    all_divs = sorted(df_full["Division"].dropna().unique())
    sel_divs = st.multiselect("Select divisions", all_divs, default=all_divs,
                               label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div style='color:#5555aa;font-size:11px;'>Data: 2025 order records</div>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_d, end_d = df_full["Order Date"].min(), df_full["Order Date"].max()

df = df_full[
    (df_full["Order Date"] >= start_d) &
    (df_full["Order Date"] <= end_d) &
    (df_full["Region"].isin(sel_regions)) &
    (df_full["Ship Mode"].isin(sel_modes)) &
    (df_full["Division"].isin(sel_divs))
].copy()

df["Delayed"] = df["Lead Time"] > threshold

# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🗺️ Geographic Map",
    "🚚 Ship Mode Analysis",
    "🔍 Route Drill-Down"
])

# ══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="page-title">Route Efficiency Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Showing <b>{len(df):,}</b> shipments · Delay threshold: >{threshold} days</div>',
                unsafe_allow_html=True)

    # KPI cards
    avg_lead  = df["Lead Time"].mean()
    delay_pct = df["Delayed"].mean() * 100
    total_orders = len(df)
    best_route = df.groupby("Route")["Lead Time"].mean().idxmin() if len(df) > 0 else "—"
    worst_route = df.groupby("Route")["Lead Time"].mean().idxmax() if len(df) > 0 else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-sub">filtered shipments</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        lt_color = "#4ade80" if avg_lead < 5 else "#facc15" if avg_lead < threshold else "#f87171"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Lead Time</div>
            <div class="metric-value" style="color:{lt_color}">{avg_lead:.1f}d</div>
            <div class="metric-sub">across all routes</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        dp_color = "#4ade80" if delay_pct < 10 else "#facc15" if delay_pct < 25 else "#f87171"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Delay Rate</div>
            <div class="metric-value" style="color:{dp_color}">{delay_pct:.1f}%</div>
            <div class="metric-sub">orders exceed {threshold}d threshold</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Routes Tracked</div>
            <div class="metric-value">{df["Route"].nunique()}</div>
            <div class="metric-sub">region → state pairs</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">Average Lead Time by Region</div>',
                    unsafe_allow_html=True)
        region_lt = (df.groupby("Region")["Lead Time"]
                     .agg(["mean", "median", "count", "std"])
                     .round(2).reset_index())
        region_lt.columns = ["Region", "Avg Days", "Median Days", "Orders", "Std Dev"]
        region_lt = region_lt.sort_values("Avg Days")

        fig = px.bar(
            region_lt, x="Region", y="Avg Days",
            color="Avg Days",
            color_continuous_scale=["#4ade80", "#facc15", "#f87171"],
            text=region_lt["Avg Days"].apply(lambda x: f"{x:.1f}d"),
            hover_data={"Orders": True, "Median Days": True, "Std Dev": True},
        )
        fig.update_traces(textposition="outside", textfont_color="#ffffff")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccff",
            xaxis=dict(gridcolor="#2e2e50"),
            yaxis=dict(gridcolor="#2e2e50", title="Days"),
            coloraxis_showscale=False,
            height=320,
            margin=dict(t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Performance Leaderboard</div>',
                    unsafe_allow_html=True)

        # Top 10 routes by volume
        route_stats = (df.groupby("Route").agg(
            avg_lt=("Lead Time", "mean"),
            orders=("Lead Time", "count"),
            delay_pct=("Delayed", "mean")
        ).reset_index())
        route_stats["Score"] = 100 - (route_stats["avg_lt"] / route_stats["avg_lt"].max() * 100)
        route_stats = route_stats.sort_values("Score", ascending=False).head(12)

        for _, row in route_stats.iterrows():
            score = row["Score"]
            chip_class = "chip-good" if score > 65 else "chip-warn" if score > 40 else "chip-bad"
            label = "Fast" if score > 65 else "OK" if score > 40 else "Slow"
            short_route = row["Route"].replace(" → ", " → ").split(" → ")
            route_short = f"{short_route[0][:3].upper()} → {short_route[-1][:12]}" if len(short_route) > 1 else row["Route"][:20]
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:8px 12px;margin-bottom:6px;
                        background:#1e1e35;border-radius:10px;border:1px solid #2e2e50;">
                <span style="color:#ccccff;font-size:13px;">{route_short}</span>
                <div>
                    <span style="color:#8888bb;font-size:12px;margin-right:8px;">{row['avg_lt']:.1f}d · {int(row['orders'])} orders</span>
                    <span class="chip {chip_class}">{label}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Lead Time Distribution</div>', unsafe_allow_html=True)

    fig2 = px.histogram(
        df, x="Lead Time", color="Region",
        nbins=40,
        color_discrete_sequence=["#818cf8", "#34d399", "#fb923c", "#f472b6"],
        barmode="overlay",
        opacity=0.75,
    )
    fig2.add_vline(x=threshold, line_dash="dash", line_color="#f87171",
                   annotation_text=f"Threshold ({threshold}d)",
                   annotation_font_color="#f87171")
    fig2.add_vline(x=avg_lead, line_dash="dot", line_color="#facc15",
                   annotation_text=f"Avg ({avg_lead:.1f}d)",
                   annotation_font_color="#facc15")
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccccff",
        xaxis=dict(gridcolor="#2e2e50", title="Lead Time (days)"),
        yaxis=dict(gridcolor="#2e2e50", title="Orders"),
        height=280, margin=dict(t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC MAP
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="page-title">Geographic Shipping Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Average lead time and delay rates by state</div>',
                unsafe_allow_html=True)

    # State abbreviation map
    state_abbr = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
        'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
        'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
        'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH',
        'New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC',
        'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA',
        'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
        'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
        'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC',
    }

    state_stats = df.groupby("State/Province").agg(
        avg_lt=("Lead Time", "mean"),
        orders=("Lead Time", "count"),
        delay_pct=("Delayed", "mean"),
        total_sales=("Sales", "sum")
    ).reset_index()
    state_stats["abbr"] = state_stats["State/Province"].map(state_abbr)
    state_stats = state_stats.dropna(subset=["abbr"])
    state_stats["delay_pct_label"] = (state_stats["delay_pct"] * 100).round(1)

    map_metric = st.radio(
        "Color map by:",
        ["Avg Lead Time (days)", "Delay Rate (%)", "Order Volume"],
        horizontal=True
    )

    if map_metric == "Avg Lead Time (days)":
        color_col, color_label, cscale = "avg_lt", "Avg Lead Time", "RdYlGn_r"
        hover_extra = {"orders": True, "delay_pct_label": True}
    elif map_metric == "Delay Rate (%)":
        color_col, color_label, cscale = "delay_pct_label", "Delay Rate %", "RdYlGn_r"
        hover_extra = {"avg_lt": ":.1f", "orders": True}
    else:
        color_col, color_label, cscale = "orders", "Order Volume", "Blues"
        hover_extra = {"avg_lt": ":.1f", "delay_pct_label": True}

    fig_map = px.choropleth(
        state_stats,
        locations="abbr",
        locationmode="USA-states",
        color=color_col,
        scope="usa",
        color_continuous_scale=cscale,
        hover_name="State/Province",
        hover_data=hover_extra,
        labels={"avg_lt": "Avg Lead Time", "orders": "Orders",
                "delay_pct_label": "Delay %", "abbr": "State"}
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="#0f0f1a",
                 landcolor="#1e1e35", subunitcolor="#2e2e50"),
        coloraxis_colorbar=dict(tickfont_color="#ccccff", title_font_color="#ccccff"),
        margin=dict(t=0, b=0, l=0, r=0),
        height=460,
        font_color="#ccccff"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Regional Bottleneck Summary</div>',
                unsafe_allow_html=True)

    region_summary = df.groupby("Region").agg(
        avg_lt=("Lead Time", "mean"),
        total_orders=("Lead Time", "count"),
        delay_pct=("Delayed", "mean"),
        states=("State/Province", "nunique"),
    ).reset_index().sort_values("avg_lt", ascending=False)

    cols = st.columns(len(region_summary))
    for i, (_, row) in enumerate(region_summary.iterrows()):
        with cols[i]:
            color = "#f87171" if row["avg_lt"] > threshold else "#facc15" if row["avg_lt"] > threshold * 0.6 else "#4ade80"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-title">{row['Region']}</div>
                <div class="metric-value" style="color:{color}">{row['avg_lt']:.1f}d</div>
                <div class="metric-sub">{int(row['total_orders']):,} orders · {row['delay_pct']*100:.0f}% delayed</div>
                <div class="metric-sub">{int(row['states'])} states served</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — SHIP MODE ANALYSIS
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="page-title">Ship Mode Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">How different shipping methods stack up on speed and reliability</div>',
                unsafe_allow_html=True)

    mode_stats = df.groupby("Ship Mode").agg(
        avg_lt=("Lead Time", "mean"),
        median_lt=("Lead Time", "median"),
        orders=("Lead Time", "count"),
        delay_pct=("Delayed", "mean"),
        std_lt=("Lead Time", "std"),
        total_sales=("Sales", "sum")
    ).reset_index().sort_values("avg_lt")

    # KPI row
    kpi_cols = st.columns(len(mode_stats))
    for i, (_, row) in enumerate(mode_stats.iterrows()):
        color = "#4ade80" if row["avg_lt"] < 4 else "#facc15" if row["avg_lt"] < 7 else "#f87171"
        with kpi_cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-title">{row['Ship Mode']}</div>
                <div class="metric-value" style="color:{color}">{row['avg_lt']:.1f}d</div>
                <div class="metric-sub">{int(row['orders']):,} orders · {row['delay_pct']*100:.0f}% delayed</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-header">Lead Time Distribution by Mode</div>',
                    unsafe_allow_html=True)
        fig_box = px.box(
            df.sort_values("Lead Time"),
            x="Ship Mode", y="Lead Time",
            color="Ship Mode",
            color_discrete_sequence=["#818cf8", "#34d399", "#fb923c", "#f472b6"],
            points="outliers"
        )
        fig_box.add_hline(y=threshold, line_dash="dash", line_color="#f87171",
                          annotation_text=f"Threshold", annotation_font_color="#f87171")
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccff",
            xaxis=dict(gridcolor="#2e2e50"),
            yaxis=dict(gridcolor="#2e2e50", title="Lead Time (days)"),
            height=340, margin=dict(t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">Volume & Delay Rate by Mode</div>',
                    unsafe_allow_html=True)
        fig_bubble = px.scatter(
            mode_stats,
            x="avg_lt", y="delay_pct",
            size="orders", color="Ship Mode",
            text="Ship Mode",
            color_discrete_sequence=["#818cf8", "#34d399", "#fb923c", "#f472b6"],
            size_max=60,
        )
        fig_bubble.update_traces(textposition="top center", textfont_color="#ffffff")
        fig_bubble.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccff",
            xaxis=dict(gridcolor="#2e2e50", title="Avg Lead Time (days)"),
            yaxis=dict(gridcolor="#2e2e50", title="Delay Rate", tickformat=".0%"),
            height=340, margin=dict(t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Mode Performance by Region</div>',
                unsafe_allow_html=True)

    heat_data = df.groupby(["Region", "Ship Mode"])["Lead Time"].mean().reset_index()
    heat_pivot = heat_data.pivot(index="Region", columns="Ship Mode", values="Lead Time")

    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale="RdYlGn_r",
        text_auto=".1f",
        aspect="auto"
    )
    fig_heat.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccccff",
        height=280, margin=dict(t=10, b=10),
        xaxis=dict(title=""), yaxis=dict(title=""),
        coloraxis_colorbar=dict(tickfont_color="#ccccff")
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 — ROUTE DRILL-DOWN
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="page-title">Route Drill-Down</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">State-level insights and individual shipment timelines</div>',
                unsafe_allow_html=True)

    d_left, d_right = st.columns([1, 2])

    with d_left:
        states = sorted(df["State/Province"].dropna().unique())
        sel_state = st.selectbox("Select a state:", states)

    state_df = df[df["State/Province"] == sel_state].copy()

    with d_right:
        s_avg  = state_df["Lead Time"].mean()
        s_del  = state_df["Delayed"].mean() * 100
        s_cnt  = len(state_df)
        s_best = state_df.loc[state_df["Lead Time"].idxmin(), "Ship Mode"] if s_cnt > 0 else "—"
        overall_avg = df["Lead Time"].mean()
        vs = s_avg - overall_avg
        vs_str = f"{'▲' if vs > 0 else '▼'} {abs(vs):.1f}d vs overall"
        vs_color = "#f87171" if vs > 0 else "#4ade80"

        c1, c2, c3 = st.columns(3)
        c1.metric("Orders", f"{s_cnt:,}")
        c2.metric("Avg Lead Time", f"{s_avg:.1f}d", delta=vs_str,
                  delta_color="inverse")
        c3.metric("Delay Rate", f"{s_del:.1f}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f'<div class="section-header">Lead Time by Ship Mode — {sel_state}</div>',
                    unsafe_allow_html=True)
        if len(state_df) > 0:
            mode_state = state_df.groupby("Ship Mode").agg(
                avg_lt=("Lead Time","mean"), orders=("Lead Time","count")
            ).reset_index().sort_values("avg_lt")
            fig_sm = px.bar(
                mode_state, x="Ship Mode", y="avg_lt",
                color="avg_lt",
                color_continuous_scale=["#4ade80","#facc15","#f87171"],
                text=mode_state["avg_lt"].apply(lambda x: f"{x:.1f}d"),
                hover_data={"orders":True}
            )
            fig_sm.update_traces(textposition="outside", textfont_color="#fff")
            fig_sm.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccccff",
                xaxis=dict(gridcolor="#2e2e50"), yaxis=dict(gridcolor="#2e2e50", title="Days"),
                coloraxis_showscale=False, height=280, margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig_sm, use_container_width=True)

    with col_b:
        st.markdown(f'<div class="section-header">Monthly Lead Time Trend — {sel_state}</div>',
                    unsafe_allow_html=True)
        if len(state_df) > 0:
            state_df["Month"] = state_df["Order Date"].dt.to_period("M").astype(str)
            monthly = state_df.groupby("Month")["Lead Time"].mean().reset_index()
            monthly.columns = ["Month", "Avg Lead Time"]
            fig_trend = px.line(
                monthly, x="Month", y="Avg Lead Time",
                markers=True,
                color_discrete_sequence=["#818cf8"]
            )
            fig_trend.add_hline(y=threshold, line_dash="dash", line_color="#f87171",
                                annotation_text="Threshold", annotation_font_color="#f87171")
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccccff",
                xaxis=dict(gridcolor="#2e2e50", tickangle=-45),
                yaxis=dict(gridcolor="#2e2e50", title="Avg Lead Time (days)"),
                height=280, margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")
    st.markdown(f'<div class="section-header">📦 Individual Shipments — {sel_state}</div>',
                unsafe_allow_html=True)

    if len(state_df) > 0:
        show_only_delayed = st.checkbox("Show only delayed shipments", value=False)
        view_df = state_df[state_df["Delayed"]] if show_only_delayed else state_df
        view_df = view_df.sort_values("Lead Time", ascending=False)

        display_cols = ["Order ID", "Order Date", "Ship Date", "Lead Time",
                        "Ship Mode", "Product Name", "Sales", "Units", "Delayed"]
        show_df = view_df[display_cols].copy()
        show_df["Order Date"] = show_df["Order Date"].dt.strftime("%b %d, %Y")
        show_df["Ship Date"]  = show_df["Ship Date"].dt.strftime("%b %d, %Y")
        show_df["Sales"] = show_df["Sales"].apply(lambda x: f"${x:.2f}")
        show_df["Lead Time"] = show_df["Lead Time"].apply(lambda x: f"{x}d")
        show_df["Delayed"] = show_df["Delayed"].map({True: "⚠️ Yes", False: "✅ No"})
        show_df = show_df.rename(columns={
            "Order ID": "Order", "Order Date": "Ordered", "Ship Date": "Shipped",
            "Lead Time": "Days", "Ship Mode": "Mode",
            "Product Name": "Product", "Delayed": "Delayed?"
        })

        st.dataframe(
            show_df.head(100),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Order": st.column_config.TextColumn(width="medium"),
                "Product": st.column_config.TextColumn(width="large"),
                "Days": st.column_config.TextColumn(width="small"),
                "Sales": st.column_config.TextColumn(width="small"),
            }
        )
        st.caption(f"Showing top {min(100, len(view_df))} of {len(view_df):,} records")
