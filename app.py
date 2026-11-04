import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine import CROPS, SOILS, STAGES, advise

st.set_page_config(page_title="JalSakhi | Irrigation advisor", page_icon="💧", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#18332b; --muted:#6d7d75; --green:#247451; --mint:#e7f3ec; --paper:#f7f8f3; }
.stApp { background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; }
.block-container { max-width:1320px; padding-top:1.5rem; padding-bottom:2rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--ink) !important; letter-spacing:-.035em; }
.brand { display:flex;align-items:center;gap:11px;font-family:Manrope,sans-serif;font-weight:800;font-size:21px;color:#18332b; }
.brand-mark { width:38px;height:38px;border-radius:13px;background:#247451;color:white;display:grid;place-items:center;font-size:19px; }
.eyebrow { font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:#537968;margin:0 0 9px; }
.hero { background:linear-gradient(118deg,#edf5ee 0%,#e2efe5 60%,#d6e9db 100%);border:1px solid #d5e7d9;border-radius:25px;padding:32px 38px;margin:24px 0 20px;position:relative;overflow:hidden; }
.hero:after { content:'🌱';position:absolute;right:4%;top:5%;font-size:118px;opacity:.13;transform:rotate(-15deg); }
.hero h1 { font-size:38px;line-height:1.15;margin:0 0 10px;max-width:670px; }
.hero p { color:#526b5d;font-size:15px;max-width:620px;margin:0;line-height:1.65; }
.card { background:#fff;border:1px solid #e6ebe5;border-radius:18px;padding:20px 22px;box-shadow:0 5px 20px rgba(24,51,43,.035); }
.metric-label { color:#76837c;font-size:12px;font-weight:600;letter-spacing:.03em; }
.metric-value { color:#18332b;font-family:Manrope,sans-serif;font-size:28px;font-weight:800;margin-top:7px; }
.metric-note { color:#78867e;font-size:12px;margin-top:3px; }
.status { border-radius:18px;padding:20px 23px;background:#e8f3e9;border:1px solid #d3e6d6; }
.status.warn { background:#fff3e5;border-color:#f1dfc4; }
.status-title { color:#1d6848;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase; }
.status.warn .status-title { color:#a36520; }
.status-action { color:#17372b;font:800 27px Manrope,sans-serif;margin:5px 0; }
.status-copy { color:#607168;font-size:13px;line-height:1.55; }
.section-label { color:#5d7567;font-size:11px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;margin:6px 0 12px; }
div[data-testid="stMetric"] { background:white;border:1px solid #e6ebe5;border-radius:16px;padding:15px 18px; }
div[data-testid="stMetricLabel"] p { color:#718078;font-size:12px;font-weight:600; }
div[data-testid="stMetricValue"] { color:#18332b;font-family:Manrope,sans-serif;font-size:25px; }
div[data-testid="stSidebar"] { background:#f1f4ef;border-right:1px solid #e4e9e2; }
div[data-testid="stSidebar"] h1 { font-size:22px; }
.fine { color:#7b8981;font-size:11px;line-height:1.6; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">💧</span>JalSakhi</div>', unsafe_allow_html=True)
    st.markdown("### Farm profile")
    st.caption("Tell us what is growing and what the field is like today.")
    crop = st.selectbox("Crop", list(CROPS), index=2)
    stage = st.selectbox("Growth stage", list(STAGES), index=2)
    soil = st.selectbox("Soil type", list(SOILS), index=1)
    acres = st.number_input("Field size (acres)", min_value=0.1, max_value=500.0, value=2.0, step=0.1)
    st.markdown("### Today's conditions")
    moisture = st.slider("Soil moisture (%)", 0, 100, 31, help="Use a sensor reading or a rough field estimate.")
    eto = st.slider("Daily heat and evaporation (mm)", 1.0, 9.0, 5.2, 0.1,
                    help="Reference evapotranspiration (ET₀). Demo value; enter a local forecast or measurement.")
    rain = st.slider("Rain expected in next 48 hours (mm)", 0.0, 80.0, 8.0, 1.0)
    st.markdown("<p class='fine'>Demo mode: all values are editable examples. No sensor or forecast service is connected.</p>", unsafe_allow_html=True)

advice = advise(crop, stage, soil, moisture, eto, rain)
st.markdown('<p class="eyebrow">Precision irrigation · GP-02 · Green Planet</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="hero"><p class="eyebrow">A little less guesswork. A lot less wasted water.</p>
<h1>Give every drop a better destination.</h1>
<p>JalSakhi combines crop stage, soil moisture, soil type and expected rain into a practical irrigation plan for your field.</p></div>
""", unsafe_allow_html=True)

left, right = st.columns([1.08, .92], gap="large")
with left:
    st.markdown('<p class="section-label">Today’s recommendation</p>', unsafe_allow_html=True)
    warn = advice.action == "Irrigate today"
    st.markdown(f"""<div class="status {'warn' if warn else ''}"><div class="status-title">{advice.urgency} · {crop} · {acres:g} acres</div>
<div class="status-action">{advice.action}</div><div class="status-copy">Apply approximately <b>{advice.gross_mm:.1f} mm</b> at the field, about <b>{advice.litres_per_acre:,} L/acre</b> ({advice.litres_per_acre * acres:,.0f} litres for this field). Recheck soil moisture after watering.</div></div>""", unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.metric("Crop water use", f"{advice.daily_need_mm:.1f} mm/day", "crop stage adjusted")
    c2.metric("Root-zone depletion", f"{advice.depletion_mm:.0f} mm", f"trigger near {advice.threshold_mm:.0f} mm")
    c3.metric("Useful forecast rain", f"{advice.effective_rain_mm:.1f} mm", "after infiltration estimate")
    st.markdown('<p class="section-label" style="margin-top:24px">Why this advice</p>', unsafe_allow_html=True)
    for reason in advice.reasons:
        st.markdown(f"- {reason}")

with right:
    st.markdown('<p class="section-label">Root-zone water balance</p>', unsafe_allow_html=True)
    cap = SOILS[soil]["available_water_mm_per_m"] * CROPS[crop]["root_depth_cm"] / 100
    stored = cap - advice.depletion_mm
    fig = go.Figure(go.Pie(values=[max(0, stored), advice.depletion_mm], hole=.76, sort=False,
        marker_colors=["#65a881", "#e7eee8"], textinfo="none", hovertemplate="%{value:.1f} mm<extra></extra>",
        direction="clockwise", rotation=270))
    fig.add_annotation(text=f"{max(0, stored):.0f}<br><span style='font-size:11px;color:#718078'>mm in root zone</span>",
                       x=.5,y=.5,showarrow=False,font=dict(size=25,color="#18332b",family="Manrope"))
    fig.update_layout(height=215,margin=dict(t=0,b=0,l=0,r=0),showlegend=False,paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.caption(f"Estimated root-zone capacity: {cap:.0f} mm · {soil.lower()} soil · {CROPS[crop]['root_depth_cm']} cm rooting depth")
    st.markdown('<p class="section-label" style="margin-top:22px">Next seven days</p>', unsafe_allow_html=True)
    weekly = pd.DataFrame(advice.weekly).set_index("Day")
    st.line_chart(weekly[["Root-zone depletion (mm)", "Crop water use (mm)"]], color=["#df9a48", "#39845e"], height=210)
    st.caption("Planning estimate only. Recheck the field if rain, irrigation, or weather changes.")

st.divider()
with st.expander("How JalSakhi makes this estimate"):
    st.markdown("""
    **Transparent water-balance logic:** crop water use = reference evapotranspiration × crop coefficient × growth-stage factor. The app estimates root-zone water capacity from soil type and crop rooting depth, estimates depletion from the moisture reading, discounts forecast rain by soil infiltration, and recommends a refill near the crop's depletion trigger.

    **What this prototype does not do:** it is not a field-calibrated ML model, does not connect to live weather or sensors, and does not account for every local variety, irrigation method, or soil condition. Confirm amounts with local agricultural guidance before using them in a real field.
    """)
st.markdown("<p class='fine'>JalSakhi is an educational prototype for the Neural Storm 2026 GP-02 challenge. Estimates are illustrative and are not a substitute for local agronomic advice.</p>", unsafe_allow_html=True)
