# utils/api_utils.py
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List

WORLD_CITIES_PATH = "data/worldcities.csv"

def valid_city(check_city: str) -> bool:
    """
    Check if a city is valid using the worldcities db.
    """
    try:
        df = pd.read_csv('data/worldcities.csv')
        return check_city.lower() in map(str.lower, df["city"].tolist())
    except Exception:
        # If the file isn't available, fall back to "non-empty string" check
        return bool(check_city and check_city.strip())

def _to_local(ts_utc: int, tz_offset_s: int) -> datetime:
    """OpenWeather timestamps are in UTC seconds. Apply offset to get local naive datetime."""
    return datetime.fromtimestamp(ts_utc + tz_offset_s, tz=timezone.utc).astimezone(tz=None).replace(tzinfo=None)

def _wind_dir_from_deg(deg: float) -> str:
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    ix = int((deg + 22.5) // 45) % 8
    return dirs[ix]

def _km_or_mi(meters: int, metric: str) -> float:
    if metric == "imperial":
        return round(meters / 1609.344, 1)  # miles
    return round(meters / 1000.0, 1)       # km

def _kph_or_mph(speed: float, metric: str) -> float:
    """OpenWeather returns m/s for metric, mph for imperial."""
    if metric == "imperial":
        return speed  # already mph
    return speed * 3.6  # m/s -> km/h

def _safe_get(d: dict, *keys, default=None):
    for k in keys:
        if d is None:
            return default
        d = d.get(k)
    return d if d is not None else default

def _aqi_estimate(lat: float, lon: float, api_key: str) -> int | None:
    """
    Use OpenWeather Air Pollution API (index 1..5). Map to a rough 0..200 style number
    so the badge feels familiar. If it fails, return None.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        r = requests.get(url, timeout=10)
        j = r.json()
        idx = _safe_get(j, "list", default=[])
        if not idx:
            return None
        aqi_1_5 = _safe_get(idx[0], "main", "aqi", default=None)
        if aqi_1_5 is None:
            return None
        # crude mapping (1..5) -> approx AQI number for a quick, readable badge
        mapping = {1: 25, 2: 50, 3: 100, 4: 150, 5: 200}
        return mapping.get(int(aqi_1_5), None)
    except Exception:
        return None

def get_weather_from_city(city: str, api_key: str, metric: str) -> Dict:
    """
    Normalized current weather for the UI.

    Returns keys:
    city, country, temp, feels_like, temp_min, temp_max, condition, icon,
    humidity, pressure, visibility, wind_speed, wind_dir, sunrise, sunset, dt, aqi
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={metric}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    j = r.json()

    tz_offset = int(_safe_get(j, "timezone", default=0))
    main = j.get("main", {})
    wind = j.get("wind", {})
    sys = j.get("sys", {})
    weather0 = (_safe_get(j, "weather", default=[{}]) or [{}])[0]
    coord = j.get("coord", {})

    # Build normalized dict
    out = {
        "city": _safe_get(j, "name", default=city.title()),
        "country": _safe_get(sys, "country", default=""),
        "temp": float(_safe_get(main, "temp", default=0.0)),
        "feels_like": float(_safe_get(main, "feels_like", default=0.0)),
        "temp_min": float(_safe_get(main, "temp_min", default=0.0)),
        "temp_max": float(_safe_get(main, "temp_max", default=0.0)),
        "condition": _safe_get(weather0, "description", default=""),
        "icon": _safe_get(weather0, "icon", default="01d"),
        "humidity": int(_safe_get(main, "humidity", default=0)),
        "pressure": int(_safe_get(main, "pressure", default=0)),
        "visibility": _km_or_mi(int(_safe_get(j, "visibility", default=0)), metric),
        "wind_speed": _kph_or_mph(float(_safe_get(wind, "speed", default=0.0)), metric),
        "wind_dir": _wind_dir_from_deg(float(_safe_get(wind, "deg", default=0.0))),
        "sunrise": _to_local(int(_safe_get(sys, "sunrise", default=0)), tz_offset),
        "sunset": _to_local(int(_safe_get(sys, "sunset", default=0)), tz_offset),
        "dt": _to_local(int(_safe_get(j, "dt", default=0)), tz_offset),
    }

    # Optional AQI badge (best effort)
    lat, lon = _safe_get(coord, "lat", default=None), _safe_get(coord, "lon", default=None)
    out["aqi"] = _aqi_estimate(lat, lon, api_key) if lat is not None and lon is not None else None
    return out

def get_forecast_from_city(city: str, api_key: str, metric: str) -> List[Dict]:
    """
    5-day / 3-hour forecast -> compact daily strip (Today + next days).
    Returns list of dicts: {label, dt, temp, icon, pop}
    """
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={metric}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    j = r.json()

    tz_offset = int(_safe_get(j, "city", "timezone", default=0))
    items = j.get("list", [])
    if not items:
        return []

    # Convert to local datetimes and bucket by date
    buckets: Dict[str, List[dict]] = {}
    for it in items:
        dt_local = _to_local(int(it["dt"]), tz_offset)
        key = dt_local.strftime("%Y-%m-%d")
        entry = {
            "dt": dt_local,
            "temp": float(_safe_get(it, "main", "temp", default=0.0)),
            "icon": _safe_get((_safe_get(it, "weather", default=[{}]) or [{}])[0], "icon", default="01d"),
            "pop": float(_safe_get(it, "pop", default=0.0)),
            "hour": dt_local.hour,
        }
        buckets.setdefault(key, []).append(entry)

    # For each day, pick the slot closest to 12:00 local
    days = []
    for day_key in sorted(buckets.keys()):
        day_entries = buckets[day_key]
        mid = min(day_entries, key=lambda e: abs(e["hour"] - 12))
        days.append(mid)

    # Build labels (Today, Tue, Wed, …)
    out = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    for idx, d in enumerate(days):
        label = "Today" if d["dt"].strftime("%Y-%m-%d") == today_str else d["dt"].strftime("%a")
        out.append({"label": label, "dt": d["dt"], "temp": d["temp"], "icon": d["icon"], "pop": d["pop"]})
    return out
