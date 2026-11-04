import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine import CROPS, SOILS, STAGES, advise

st.set_page_config(page_title="JalSakhi | Irrigation advisor", page_icon="💧", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --ink:#172b25; --muted:#718078; --green:#17734f; --green-dark:#0f4939;
  --lime:#c6ed77; --paper:#f5f7f3; --line:#e6ebe5; --white:#fff;
}
.stApp { background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; }
.block-container { max-width:1380px; padding-top:1.5rem; padding-bottom:2.6rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--ink) !important; letter-spacing:-.035em; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"] { right:1rem; }
div[data-testid="stSidebar"] { background:#fbfcfa; border-right:1px solid var(--line); }
div[data-testid="stSidebar"] > div:first-child { padding-top:1.4rem; }
div[data-testid="stSidebar"] h2 { font-family:'Manrope',sans-serif; font-size:15px; letter-spacing:-.02em; }
div[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color:#41544a; font-weight:600; font-size:12px; }
div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:var(--muted); }
div[data-testid="stSidebar"] [data-testid="stSelectbox"],
div[data-testid="stSidebar"] [data-testid="stNumberInput"] { margin-bottom:.35rem; }
.brand { display:flex; align-items:center; gap:10px; font-family:'Manrope',sans-serif; font-weight:800; font-size:19px; color:var(--ink); }
.brand-mark { width:36px; height:36px; border-radius:12px; background:var(--green-dark); color:white; display:grid; place-items:center; font-size:18px; box-shadow:0 5px 12px #0f493922; }
.side-note { background:#f0f5ef; border:1px solid #e3ebe1; border-radius:14px; padding:12px 13px; color:#64756b; font-size:11px; line-height:1.55; margin-top:14px; }
.topline { display:flex; justify-content:space-between; align-items:center; margin:0 0 14px; color:#76857c; font-size:12px; }
.topline span:first-child { text-transform:uppercase; letter-spacing:.14em; font-weight:700; }
.live-pill { display:inline-flex; gap:7px; align-items:center; background:#eaf4e7; color:#286244; border:1px solid #dbead7; border-radius:999px; padding:7px 11px; font-size:11px; font-weight:700; }
.live-dot { width:7px; height:7px; border-radius:50%; background:#52a56a; box-shadow:0 0 0 3px #52a56a22; }
.hero { background:radial-gradient(circle at 88% 10%,#2b7556 0,transparent 26%),linear-gradient(118deg,#103e32 0%,#15543e 58%,#1a6045 100%); border:1px solid #1d5a43; border-radius:24px; padding:30px 34px; margin:0 0 21px; position:relative; overflow:hidden; box-shadow:0 14px 36px #153f2b18; }
.hero:after { content:'✳'; position:absolute; right:8%; top:-35px; color:#bfe877; font-size:180px; opacity:.14; transform:rotate(-18deg); }
.hero-content { position:relative; z-index:1; max-width:760px; }
.hero-tag { display:inline-flex; align-items:center; gap:7px; color:#d8efc4; background:#ffffff13; border:1px solid #ffffff22; border-radius:999px; padding:6px 10px; font-size:10px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:14px; }
.hero h1 { color:#fff !important; font-size:36px; line-height:1.12; margin:0 0 10px; max-width:650px; }
.hero p { color:#d1e2d8; font-size:14px; line-height:1.65; max-width:620px; margin:0; }
.hero-foot { display:flex; gap:8px; flex-wrap:wrap; margin-top:19px; }
.hero-chip { color:#edf5ee; background:#ffffff12; border:1px solid #ffffff20; border-radius:10px; padding:7px 10px; font-size:11px; }
.panel { background:#fff; border:1px solid var(--line); border-radius:19px; padding:19px 20px; box-shadow:0 5px 22px #19392a08; }
.panel-title { display:flex; align-items:center; justify-content:space-between; margin:0 0 14px; color:#31483d; font-family:'Manrope',sans-serif; font-size:14px; font-weight:800; letter-spacing:-.02em; }
.panel-sub { color:#859188; font-family:'DM Sans',sans-serif; font-size:11px; font-weight:500; letter-spacing:0; }
.status { border-radius:16px; padding:18px 19px; background:#edf6e8; border:1px solid #dcebd3; margin-bottom:15px; }
.status.warn { background:#fff5e9; border-color:#f0dfc5; }
.status-top { display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; }
.status-title { color:#4b7557; font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.status.warn .status-title { color:#a46c2a; }
.urgency { color:#3e7050; background:#ffffffa8; border-radius:999px; padding:5px 9px; font-size:10px; font-weight:700; }
.status.warn .urgency { color:#a46c2a; }
.status-action { color:#17372b; font:800 25px Manrope,sans-serif; letter-spacing:-.04em; margin:8px 0 5px; }
.status-copy { color:#627267; font-size:12px; line-height:1.6; }
.status-copy b { color:#263c30; }
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:9px; margin:0 0 15px; }
.stat { background:#fafbf9; border:1px solid #edf0eb; border-radius:14px; padding:12px 13px; }
.stat-label { color:#829087; font-size:10px; font-weight:700; letter-spacing:.04em; }
.stat-value { color:#1d3529; font:800 19px Manrope,sans-serif; margin-top:6px; letter-spacing:-.03em; }
.stat-note { color:#8b968f; font-size:10px; margin-top:2px; }
.reason { display:flex; gap:9px; align-items:flex-start; color:#58695f; font-size:12px; line-height:1.55; padding:8px 1px; border-top:1px solid #eef1ed; }
.reason:first-child { border-top:0; }
.reason-icon { color:#2c8158; font-size:13px; }
.chart-card { background:#fff; border:1px solid var(--line); border-radius:19px; padding:18px 18px 12px; box-shadow:0 5px 22px #19392a08; }
.chart-note { color:#87928b; font-size:10px; line-height:1.5; margin-top:2px; }
div[data-testid="stPlotlyChart"] { margin-top:-4px; }
div[data-testid="stExpander"] { border:1px solid var(--line); border-radius:15px; background:#fff; }
div[data-testid="stExpander"] summary p { font-weight:700; color:#31483d; }
.fine { color:#8b968f; font-size:10px; line-height:1.6; }
@media (max-width:800px) { .hero { padding:24px 22px; } .hero h1 { font-size:29px; } .stat-grid { grid-template-columns:1fr; } .topline { align-items:flex-start; gap:10px; flex-direction:column; } }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">💧</span>JalSakhi</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Field profile")
    st.caption("Set up the field you want to plan for.")
    crop = st.selectbox("Crop", list(CROPS), index=2)
    stage = st.selectbox("Growth stage", list(STAGES), index=2)
    soil = st.selectbox("Soil type", list(SOILS), index=1)
    acres = st.number_input("Field size (acres)", min_value=0.1, max_value=500.0, value=2.0, step=0.1)
    st.markdown("## Current conditions")
    moisture = st.slider("Soil moisture (%)", 0, 100, 31, help="Use a sensor reading or a rough field estimate.")
    eto = st.slider("Daily heat and evaporation (mm)", 1.0, 9.0, 5.2, 0.1,
                    help="Reference evapotranspiration (ET₀). Demo value; enter a local forecast or measurement.")
    rain = st.slider("Rain expected in next 48 hours (mm)", 0.0, 80.0, 8.0, 1.0)
    st.markdown('<div class="side-note"><b>Demo mode</b><br>Values are editable examples. No sensor or live forecast service is connected.</div>', unsafe_allow_html=True)

advice = advise(crop, stage, soil, moisture, eto, rain)
st.markdown('''<div class="topline"><span>Precision irrigation · Green Planet</span><span class="live-pill"><i class="live-dot"></i>Interactive field planner</span></div>''', unsafe_allow_html=True)
st.markdown(f"""
<div class="hero"><div class="hero-content">
<div class="hero-tag">💧 Neural Storm 2026 · GP-02</div>
<h1>Give every drop a better destination.</h1>
<p>Make a clearer irrigation plan with crop stage, soil moisture, soil type and expected rain — and see the reasoning behind every recommendation.</p>
<div class="hero-foot"><span class="hero-chip">🌱 {crop}</span><span class="hero-chip">📍 {acres:g} acres</span><span class="hero-chip">🌦️ {rain:g} mm expected rain</span></div>
</div></div>
""", unsafe_allow_html=True)

left, right = st.columns([1.08, .92], gap="medium")
with left:
    warn = advice.action == "Irrigate today"
    st.markdown(f"""<div class="panel"><div class="panel-title">Your irrigation plan <span class="panel-sub">Today</span></div>
    <div class="status {'warn' if warn else ''}"><div class="status-top"><div class="status-title">{crop} · {stage}</div><span class="urgency">{advice.urgency}</span></div>
    <div class="status-action">{advice.action}</div><div class="status-copy">Apply approximately <b>{advice.gross_mm:.1f} mm</b> at the field — about <b>{advice.litres_per_acre:,} L/acre</b> or <b>{advice.litres_per_acre * acres:,.0f} litres</b> for this field. Recheck soil moisture after watering.</div></div>
    <div class="stat-grid"><div class="stat"><div class="stat-label">CROP WATER USE</div><div class="stat-value">{advice.daily_need_mm:.1f} mm</div><div class="stat-note">per day · stage adjusted</div></div>
    <div class="stat"><div class="stat-label">ROOT-ZONE DEPLETION</div><div class="stat-value">{advice.depletion_mm:.0f} mm</div><div class="stat-note">trigger near {advice.threshold_mm:.0f} mm</div></div>
    <div class="stat"><div class="stat-label">USEFUL FORECAST RAIN</div><div class="stat-value">{advice.effective_rain_mm:.1f} mm</div><div class="stat-note">after infiltration estimate</div></div></div>
    <div class="panel-title">Why this advice <span class="panel-sub">Based on your inputs</span></div>""", unsafe_allow_html=True)
    for reason in advice.reasons:
        st.markdown(f'<div class="reason"><span class="reason-icon">✦</span><span>{reason}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    cap = SOILS[soil]["available_water_mm_per_m"] * CROPS[crop]["root_depth_cm"] / 100
    stored = cap - advice.depletion_mm
    fig = go.Figure(go.Pie(values=[max(0, stored), advice.depletion_mm], hole=.78, sort=False,
        marker_colors=["#49a676", "#edf1ec"], textinfo="none", hovertemplate="%{value:.1f} mm<extra></extra>",
        direction="clockwise", rotation=270))
    fig.add_annotation(text=f"{max(0, stored):.0f}<br><span style='font-size:10px;color:#87928b'>mm available</span>",
                       x=.5,y=.5,showarrow=False,font=dict(size=24,color="#18332b",family="Manrope"))
    fig.update_layout(height=200,margin=dict(t=5,b=0,l=0,r=0),showlegend=False,paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="chart-card"><div class="panel-title">Root-zone water balance <span class="panel-sub">Current estimate</span></div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown(f'<div class="chart-note">Estimated capacity: {cap:.0f} mm · {soil.lower()} soil · {CROPS[crop]["root_depth_cm"]} cm rooting depth</div></div>', unsafe_allow_html=True)
    st.write("")
    weekly = pd.DataFrame(advice.weekly).set_index("Day")
    st.markdown('<div class="chart-card"><div class="panel-title">Next seven days <span class="panel-sub">Planning outlook</span></div>', unsafe_allow_html=True)
    st.line_chart(weekly[["Root-zone depletion (mm)", "Crop water use (mm)"]], color=["#d89b48", "#39845e"], height=200)
    st.markdown('<div class="chart-note">Recheck the field if rain, irrigation, or weather changes.</div></div>', unsafe_allow_html=True)

st.write("")
with st.expander("How JalSakhi makes this estimate"):
    st.markdown("""
    **Transparent water-balance logic:** crop water use = reference evapotranspiration × crop coefficient × growth-stage factor. The app estimates root-zone water capacity from soil type and crop rooting depth, estimates depletion from the moisture reading, discounts forecast rain by soil infiltration, and recommends a refill near the crop's depletion trigger.

    **What this prototype does not do:** it is not a field-calibrated ML model, does not connect to live weather or sensors, and does not account for every local variety, irrigation method, or soil condition. Confirm amounts with local agricultural guidance before using them in a real field.
    """)
st.markdown("<p class='fine'>JalSakhi · Team Error 007 · Neural Storm 2026 GP-02. Estimates are illustrative and are not a substitute for local agronomic advice.</p>", unsafe_allow_html=True)
