# app.py — Minimal Weather UI for Streamlit
import streamlit as st
from datetime import datetime
from typing import Dict, List

# -------------------------
# Page + Theme
# -------------------------
st.set_page_config(
    page_title="Weather",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ACCENT = "#4F46E5"  # indigo-600
BG = "#0B0B0C"      # near-black
CARD = "#121214"    # dark card
MUTED = "#9CA3AF"   # gray-400
OK_BADGE = "#10B981" # green-500
WARN_BADGE = "#F59E0B" # amber-500

# -------------------------
# Minimal CSS
# -------------------------
st.markdown(
    f"""
    <style>
      html, body, [class*="stApp"] {{
        background: linear-gradient(180deg, {BG} 0%, #0E0E12 100%) !important;
        color: #E5E7EB;
        font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Inter, system-ui;
      }}
      .wrap {{
        max-width: 760px; margin: 2rem auto 5rem; padding: 0 1rem;
      }}
      .header {{
        display: flex; align-items: center; gap: .75rem; margin-bottom: 1rem;
      }}
      .brand {{
        font-weight: 700; letter-spacing: .3px; opacity:.95;
      }}
      .searchbar {{
        display:flex; gap:.5rem; margin: 1rem 0 1.25rem;
      }}
      .card {{
        background: {CARD}; border: 1px solid rgba(255,255,255,.06);
        border-radius: 20px; padding: 1.25rem 1.25rem; box-shadow: 0 10px 30px rgba(0,0,0,.35);
      }}
      .cityline {{
        display:flex; align-items: baseline; justify-content: space-between; gap:1rem;
        margin-bottom:.35rem;
      }}
      .city {{
        font-size: 1.25rem; font-weight: 600;
      }}
      .updated {{
        color:{MUTED}; font-size:.85rem;
      }}
      .bigtemp {{
        font-size: 4rem; font-weight: 700; line-height: 1; margin:.25rem 0 .5rem;
      }}
      .cond {{
        color:{MUTED}; font-size: 1rem; margin-bottom:.75rem;
      }}
      .grid {{
        display:grid; grid-template-columns: repeat(4, minmax(0,1fr));
        gap:.75rem; margin-top:.5rem;
      }}
      .kv {{
        background: rgba(255,255,255,.02);
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 14px; padding:.85rem;
      }}
      .k {{
        color:{MUTED}; font-size:.8rem; margin-bottom:.15rem;
      }}
      .v {{
        font-weight:600; font-size:1.05rem;
      }}
      .forecast {{
        display:flex; gap:.6rem; overflow-x:auto; padding-bottom:.25rem; margin-top:1rem;
      }}
      .fcard {{
        min-width: 92px; text-align:center; padding:.8rem; border-radius:14px;
        background: rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.06);
      }}
      .tag {{
        display:inline-flex; align-items:center; gap:.4rem; font-size:.75rem;
        padding:.2rem .55rem; border-radius: 999px; border: 1px solid rgba(255,255,255,.12);
      }}
      .ok {{ color:{OK_BADGE}; border-color: rgba(16,185,129,.35); }}
      .warn {{ color:{WARN_BADGE}; border-color: rgba(245,158,11,.35); }}
      .accent {{ color:{ACCENT}; }}
      .small {{ font-size:.85rem; color:{MUTED}; }}
      .spacer {{ height: .25rem; }}
      /* hide streamlit chrome we don't need */
      header [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{ display:none; }}
      .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Replace these with your real functions
# -------------------------
def get_weather(city: str, units: str) -> Dict:
    """
    Return your parsed *current* weather dict with at least keys:
    city, country, temp, feels_like, condition, icon, humidity, wind_kph, wind_dir,
    pressure_hpa, visibility_km, sunrise, sunset, dt (timestamp), aqi (optional).
    """
    # --- placeholder sample; plug your OpenWeather response here ---
    now = datetime.utcnow()
    return {
        "city": city.title(),
        "country": "IN",
        "temp": 29.4 if units=="metric" else 85.0,
        "feels_like": 32.0 if units=="metric" else 89.6,
        "condition": "Partly cloudy",
        "icon": "02d",  # OpenWeather icon code
        "humidity": 68,
        "wind_kph": 9,
        "wind_dir": "SW",
        "pressure_hpa": 1004,
        "visibility_km": 8,
        "sunrise": now.replace(hour=0, minute=15),
        "sunset":  now.replace(hour=12, minute=35),
        "dt": now,
        "aqi": 62,  # optional
    }

def get_forecast(city: str, units: str) -> List[Dict]:
    """
    Return a list of small forecast dicts with: dt, temp, icon, pop (precip prob), label
    """
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    out = []
    for i in range(8):  # next 8 slots (e.g., 3-hourly or daily—your pick)
        out.append({
            "dt": now,
            "temp": 26 + i*0.4 if units=="metric" else 78 + i,
            "icon": "02d",
            "pop": 0.1 if i%3 else 0.4,
            "label": (now.strftime("%a") if i else "Today"),
        })
        now = now.replace(day=now.day)  # (placeholder; use real timestamps)
    return out

# -------------------------
# UI helpers
# -------------------------
def icon_url(code: str) -> str:
    return f"https://openweathermap.org/img/wn/{code}@2x.png"

def format_clock(dt: datetime) -> str:
    try:
        return dt.strftime("%-I:%M %p")
    except:
        return dt.strftime("%I:%M %p").lstrip("0")

def aqi_badge(aqi: int) -> str:
    klass = "ok" if aqi <= 100 else "warn"
    return f'<span class="tag {klass}">AQI {aqi}</span>'

def feels_badge(temp: float, feels: float, units: str) -> str:
    delta = feels - temp
    if abs(delta) < 1.0:
        return '<span class="tag">Feels normal</span>'
    label = "Warmer" if delta > 0 else "Cooler"
    return f'<span class="tag {"warn" if delta>2 else ""}">{label} by {abs(delta):.0f}°{"C" if units=="metric" else "F"}</span>'

# -------------------------
# Sidebar (compact)
# -------------------------
with st.sidebar:
    st.markdown("### settings")
    units = st.radio("Units", ["metric", "imperial"], horizontal=True, index=0, label_visibility="collapsed")
    st.caption("Units")
    st.divider()
    st.caption("Tip: press ⏎ to search")

# -------------------------
# Header + Search
# -------------------------
st.markdown('<div class="wrap">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="header">
      <span>🌤️</span>
      <div class="brand">weather</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([4,1])
with col1:
    city = st.text_input("City", value="Bengaluru", label_visibility="collapsed", placeholder="Search city…")
with col2:
    search = st.button("Search", use_container_width=True)

if search or city:
    data = get_weather(city.strip(), units)
    fcst = get_forecast(city.strip(), units)

    # -------------------------
    # Current Conditions Card
    # -------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # City + Updated line
    left, right = st.columns([3,2])
    with left:
        st.markdown(
            f"""
            <div class="cityline">
              <div class="city">{data["city"]}, {data["country"]}</div>
              <div class="updated small">Updated {data["dt"].strftime("%b %d, %I:%M %p")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        # badges
        tags = []
        if "aqi" in data and data["aqi"] is not None:
            tags.append(aqi_badge(int(data["aqi"])))
        tags.append(feels_badge(float(data["temp"]), float(data["feels_like"]), units))
        st.markdown(" ".join(tags), unsafe_allow_html=True)

    # Temp + condition row
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown(f'<div class="bigtemp">{data["temp"]:.0f}°{"C" if units=="metric" else "F"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cond">{data["condition"]}</div>', unsafe_allow_html=True)
    with c2:
        st.image(icon_url(data["icon"]), width=92)

    # Key metrics grid
    st.markdown('<div class="grid">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="kv"><div class="k">Feels like</div><div class="v">{data["feels_like"]:.0f}°</div></div>
        <div class="kv"><div class="k">Humidity</div><div class="v">{data["humidity"]}%</div></div>
        <div class="kv"><div class="k">Wind</div><div class="v">{data["wind_kph"]} km/h {data["wind_dir"]}</div></div>
        <div class="kv"><div class="k">Pressure</div><div class="v">{data["pressure_hpa"]} hPa</div></div>
        <div class="kv"><div class="k">Visibility</div><div class="v">{data["visibility_km"]} km</div></div>
        <div class="kv"><div class="k">Sunrise</div><div class="v">{format_clock(data["sunrise"])}</div></div>
        <div class="kv"><div class="k">Sunset</div><div class="v">{format_clock(data["sunset"])}</div></div>
        <div class="kv"><div class="k">Units</div><div class="v">{"Metric (°C)" if units=="metric" else "Imperial (°F)"}</div></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)  # /grid
    st.markdown('</div>', unsafe_allow_html=True)  # /card

    # -------------------------
    # Forecast row
    # -------------------------
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small">Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="forecast">', unsafe_allow_html=True)
    # Render small forecast cards
    for f in fcst:
        pop = int(round(f["pop"] * 100))
        st.markdown(
            f"""
            <div class="fcard">
                <div class="small">{f["label"]}</div>
                <img src="{icon_url(f["icon"])}" width="64" />
                <div class="v" style="margin-top:.1rem">{f["temp"]:.0f}°</div>
                <div class="small">{pop}% rain</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)  # /forecast
    st.markdown('</div>', unsafe_allow_html=True)  # /card

st.markdown('</div>', unsafe_allow_html=True)  # /wrap
