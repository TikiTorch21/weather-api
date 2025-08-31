# app.py — Minimal Weather UI for Streamlit (matches the mock)
import streamlit as st
from datetime import datetime
from utils.api_utils import (
    get_weather_from_city,
    get_forecast_from_city,
    valid_city,
)
from config import API_KEY

# -------------------------
# Page + Theme
# -------------------------
st.set_page_config(
    page_title="Weather",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ACCENT = "#4F46E5"   # indigo-600
BG_DEFAULT = "#0B0B0C"
CARD = "#121214"     # dark card
MUTED = "#9CA3AF"    # gray-400
OK_BADGE = "#10B981" # green-500
WARN_BADGE = "#F59E0B" # amber-500

# -------------------------
# Minimal CSS
# -------------------------
st.markdown(
    f"""
    <style>
      html, body, [class*="stApp"] {{
          background: linear-gradient(
        180deg,
        var(--bg-top, #0B0B0C) 0%,
        var(--bg-bottom, #0E0E12) 100%
        ) !important;
        color: #E5E7EB;
        font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Inter, system-ui;
      }}
      .wrap {{ max-width: 760px; margin: 2rem auto 5rem; padding: 0 1rem; }}
      .header {{ display: flex; align-items: center; gap: .75rem; margin-bottom: 1rem; }}
      .brand {{ font-weight: 700; letter-spacing: .3px; opacity:.95; }}
      .card {{
        background: {CARD}; border: 1px solid rgba(255,255,255,.06);
        border-radius: 20px; padding: 1.25rem 1.25rem; box-shadow: 0 10px 30px rgba(0,0,0,.35);
      }}
      .cityline {{
        display:flex; align-items: baseline; justify-content: space-between; gap:1rem; margin-bottom:.35rem;
      }}
      .city {{ font-size: 1.25rem; font-weight: 600; }}
      .updated {{ color:{MUTED}; font-size:.85rem; }}
      .bigtemp {{ font-size: 4rem; font-weight: 700; line-height: 1; margin:.25rem 0 .5rem; }}
      .cond {{ color:{MUTED}; font-size: 1rem; margin-bottom:.75rem; }}
      .grid {{
        display:grid; grid-template-columns: repeat(4, minmax(0,1fr));
        gap:.75rem; margin-top:.5rem;
      }}
      .kv {{
        background: rgba(255,255,255,.02);
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 14px; padding:.85rem;
      }}
      .k {{ color:{MUTED}; font-size:.8rem; margin-bottom:.15rem; }}
      .v {{ font-weight:600; font-size:1.05rem; }}
      .forecast {{ display:flex; gap:.6rem; overflow-x:auto; padding-bottom:.25rem; margin-top:1rem; }}
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
      .small {{ font-size:.85rem; color:{MUTED}; }}
      header [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{ display:none; }}
      .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
      .searchrow {{ display:flex; gap:.5rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helpers (UI-only)
# -------------------------
def icon_url(code: str) -> str:
    return f"https://openweathermap.org/img/wn/{code}@2x.png"

def fmt_clock(dt: datetime) -> str:
    # Cross-platform hour w/out leading zero
    try:
        return dt.strftime("%-I:%M %p")
    except Exception:
        return dt.strftime("%I:%M %p").lstrip("0")

def aqi_badge(aqi: int | None) -> str:
    if aqi is None:
        return ""
    klass = "ok" if aqi <= 100 else "warn"
    return f'<span class="tag {klass}">AQI {aqi}</span>'

def feels_badge(temp: float, feels: float, unit: str) -> str:
    delta = feels - temp
    if abs(delta) < 1.0:
        return '<span class="tag">Feels normal</span>'
    label = "Warmer" if delta > 0 else "Cooler"
    warn = ' warn' if delta > 2 else ''
    suffix = "°C" if unit == "metric" else "°F"
    return f'<span class="tag{warn}">{label} by {abs(delta):.0f}{suffix}</span>'

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("### Settings")
    unit = st.radio("Units", ["Celsius", "Fahrenheit"], horizontal=True, index=0)
    st.caption("Tip: press ⏎ to search")

metric_dict = {"Celsius": "metric", "Fahrenheit": "imperial"}
metric = metric_dict.get(unit, "metric")

# -------------------------
# Header + Search
# -------------------------
st.markdown('<div class="wrap">', unsafe_allow_html=True)
st.markdown('<div class="header"><span>🌤️</span><div class="brand">weather</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([4,1])
with col1:
    city = st.text_input("City", value="Bengaluru", label_visibility="collapsed", placeholder="Search city…")
with col2:
    search = st.button("Search", use_container_width=True)

# -------------------------
# Main
# -------------------------
if (search or city) and city.strip():
    city_str = city.strip()

    if not valid_city(city_str):
        st.error("Please enter a valid city…")
    else:
        try:
            data = get_weather_from_city(city=city_str, api_key=API_KEY, metric=metric)
            # Map OpenWeather icon families to colors
            bg_top = {
                "01": "#0B1120",  # clear
                "02": "#0E1424",  # few clouds
                "03": "#0E1626",  # scattered clouds
                "04": "#0A0E16",  # overcast
                "09": "#0A0F18",  # shower rain
                "10": "#0A0F1B",  # rain
                "11": "#090A12",  # thunderstorm
                "13": "#0E1726",  # snow
                "50": "#111827",  # mist/haze
            }.get(data.get("icon","")[:2], "#0B0B0C")

            # Slightly darker at night
            if str(data.get("icon","")).endswith("n"):
                bg_top = "#0A0B0E"

            bg_bottom = "#0E0E12"  # keep a consistent bottom gradient

            # Update CSS variables so the earlier rule picks them up
            st.markdown(
                f"<style>:root{{--bg-top:{bg_top};--bg-bottom:{bg_bottom};}}</style>",
                unsafe_allow_html=True,
            )


            fcst = get_forecast_from_city(city=city_str, api_key=API_KEY, metric=metric)

            # --- Current Conditions Card ---
            st.markdown('<div class="card">', unsafe_allow_html=True)

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
                tags = []
                tags.append(feels_badge(data["temp"], data["feels_like"], metric))
                if data.get("aqi") is not None:
                    tags.append(aqi_badge(data["aqi"]))
                st.markdown(" ".join(tags), unsafe_allow_html=True)

            c1, c2 = st.columns([2,1])
            with c1:
                suffix = "C" if metric == "metric" else "F"
                st.markdown(f'<div class="bigtemp">{data["temp"]:.0f}°{suffix}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cond">{data["condition"]}</div>', unsafe_allow_html=True)
            with c2:
                st.image(icon_url(data["icon"]), width=96)

            # Key metrics grid
            wind_unit = "km/h" if metric == "metric" else "mph"
            vis_unit = "km" if metric == "metric" else "mi"
            st.markdown('<div class="grid">', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="kv"><div class="k">Feels like</div><div class="v">{data["feels_like"]:.0f}°</div></div>
                <div class="kv"><div class="k">Humidity</div><div class="v">{data["humidity"]}%</div></div>
                <div class="kv"><div class="k">Wind</div><div class="v">{data["wind_speed"]:.0f} {wind_unit} {data["wind_dir"]}</div></div>
                <div class="kv"><div class="k">Pressure</div><div class="v">{data["pressure"]} hPa</div></div>
                <div class="kv"><div class="k">Visibility</div><div class="v">{data["visibility"]:.1f} {vis_unit}</div></div>
                <div class="kv"><div class="k">Sunrise</div><div class="v">{fmt_clock(data["sunrise"])}</div></div>
                <div class="kv"><div class="k">Sunset</div><div class="v">{fmt_clock(data["sunset"])}</div></div>
                <div class="kv"><div class="k">Units</div><div class="v">{'Metric (°C)' if metric=='metric' else 'Imperial (°F)'}</div></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)  # /card

            # --- Forecast strip ---
            if fcst:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="small">Forecast</div>', unsafe_allow_html=True)
                st.markdown('<div class="forecast">', unsafe_allow_html=True)
                for f in fcst[:7]:
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

        except Exception as e:
            st.error("Something went wrong fetching weather data. Please try another city or later.")
else:
    st.caption("Enter a city to get started.")
st.markdown('</div>', unsafe_allow_html=True)  # /wrap
