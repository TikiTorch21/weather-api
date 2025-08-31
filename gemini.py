import streamlit as st
import requests
from datetime import datetime

# --- API Configuration (Replace with your actual key and utils) ---
API_KEY = "5bd25bdfe8ef3e8d7036162b2e329230" 

# --- API Helper Functions ---
def valid_city(city, api_key):
    """Checks if a city is valid by making a quick API call."""
    if not city:
        return False
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key}
    try:
        response = requests.get(base_url, params=params)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_weather_from_city(city, api_key, metric):
    """Fetches and processes weather data from the API."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": metric}
    try:
        response = requests.get(base_url, params=params).json()
        weather_dict = {
            "city": response.get("name"),
            "temp": response["main"]["temp"],
            "feels_like": response["main"]["feels_like"],
            "humidity": response["main"]["humidity"],
            "wind_speed": response["wind"]["speed"],
            "description": response["weather"][0]["description"].capitalize(),
            "icon_id": response["weather"][0]["id"]
        }
        return weather_dict
    except (requests.exceptions.RequestException, KeyError):
        return None

# --- UI Styling and Helper Functions ---

def get_background_and_text_color(icon_id):
    """Returns a background gradient and text/card colors based on weather conditions."""
    # Default to a neutral theme
    style = {
        "background": "linear-gradient(to top, #dfe9f3 0%, white 100%)",
        "text_color": "#333333",
        "card_background": "rgba(255, 255, 255, 0.7)",
        "card_text_color": "#333333"
    }

    if icon_id is None:
        return style

    if 200 <= icon_id < 300:  # Thunderstorm
        style.update({
            "background": "linear-gradient(to top, #2c3e50 0%, #4ca1af 100%)",
            "text_color": "#ffffff", "card_background": "rgba(0, 0, 0, 0.3)", "card_text_color": "#ffffff"
        })
    elif 300 <= icon_id < 600:  # Drizzle/Rain
        style.update({
            "background": "linear-gradient(to top, #6b778d 0%, #a3b8c2 100%)",
            "text_color": "#ffffff", "card_background": "rgba(0, 0, 0, 0.2)", "card_text_color": "#ffffff"
        })
    elif 600 <= icon_id < 700:  # Snow
        style.update({
            "background": "linear-gradient(to top, #e6e9f0 0%, #eef1f5 100%)",
            "text_color": "#333333", "card_background": "rgba(255, 255, 255, 0.6)", "card_text_color": "#333333"
        })
    elif 700 <= icon_id < 800:  # Atmosphere
        style.update({
            "background": "linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%)",
            "text_color": "#333333", "card_background": "rgba(255, 255, 255, 0.7)", "card_text_color": "#333333"
        })
    elif icon_id == 800:  # Clear
        style.update({
            "background": "linear-gradient(to top, #f3d9a5 0%, #a7d7f9 100%)",
            "text_color": "#333333", "card_background": "rgba(255, 255, 255, 0.5)", "card_text_color": "#333333"
        })
    elif icon_id > 800:  # Clouds
        style.update({
            "background": "linear-gradient(to top, #bdc3c7 0%, #2c3e50 60%)",
            "text_color": "#ffffff", "card_background": "rgba(0, 0, 0, 0.2)", "card_text_color": "#ffffff"
        })
    return style

def load_css(style_config):
    """Injects custom CSS for styling the app dynamically."""
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
            
            body {{ font-family: 'Poppins', sans-serif; }}
            .main {{ background: {style_config['background']}; transition: background 0.5s ease; }}
            .stApp > header, footer {{ visibility: hidden; }}
            .main .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
            h1 {{ color: {style_config['text_color']}; }}
            .stRadio [role="radiogroup"] {{ color: {style_config['text_color']}; }}

            .weather-card {{
                background: {style_config['card_background']}; color: {style_config['card_text_color']};
                border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px;
                padding: 2rem; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
                backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
            }}
            .temperature {{ font-size: 5rem; font-weight: 700; text-align: center; }}
            .city-name {{ font-size: 2.5rem; font-weight: bold; margin-bottom: -10px; }}
            .weather-description {{ text-align: center; font-size: 1.25rem; margin-top: -15px; }}
            .date-text, .detail-label {{ color: {style_config['card_text_color']}; opacity: 0.7; }}
            .details-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
                text-align: center; margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.2);
                padding-top: 1.5rem; }}
            .detail-item p {{ margin: 0; }}
            .detail-value {{ font-weight: bold; font-size: 1.1rem; }}
        </style>
    """, unsafe_allow_html=True)

def get_weather_emoji(icon_id):
    """Maps OpenWeatherMap icon IDs to a suitable emoji."""
    if 200 <= icon_id < 300: return "⛈️"
    elif 300 <= icon_id < 500: return "🌦️"
    elif 500 <= icon_id < 600: return "🌧️"
    elif 600 <= icon_id < 700: return "❄️"
    elif 700 <= icon_id < 800: return "🌫️"
    elif icon_id == 800: return "☀️"
    elif icon_id == 801: return "🌤️"
    elif icon_id > 801: return "☁️"
    else: return "🌡️"

# --- Streamlit App Layout ---

st.set_page_config(page_title="Minimal Weather", layout="centered")

# Initialize session state for styling
if 'style' not in st.session_state:
    st.session_state.style = get_background_and_text_color(None)

# Load CSS based on the current session state
load_css(st.session_state.style)

st.markdown("<h1 style='text-align: center;'>Weather Search</h1>", unsafe_allow_html=True)

with st.form("search_form"):
    city = st.text_input('Enter a city name:', placeholder='e.g., London, Tokyo, Bengaluru', label_visibility="collapsed")
    col1, col2 = st.columns([3, 1])
    with col1:
        unit = st.radio("Unit:", options=["Celsius", "Fahrenheit"], horizontal=True, label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("Search")

metric = "metric" if unit == "Celsius" else "imperial"
temp_symbol = "°C" if unit == "Celsius" else "°F"

# --- Main Logic ---

if submitted and city:
    if valid_city(city, API_KEY):
        weather_dict = get_weather_from_city(city=city, api_key=API_KEY, metric=metric)
        if weather_dict:
            new_style = get_background_and_text_color(weather_dict["icon_id"])
            if new_style != st.session_state.style:
                st.session_state.style = new_style
                st.rerun()

            # --- Display Weather Card ---
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="city-name">{weather_dict["city"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="date-text">{datetime.now().strftime("%A, %B %d")}</p>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<p class="temperature">{weather_dict["temp"]:.0f}{temp_symbol}</p>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<p style="font-size: 6rem; text-align: center; margin-top: -1rem;">{get_weather_emoji(weather_dict["icon_id"])}</p>', unsafe_allow_html=True)
            
            st.markdown(f'<p class="weather-description">{weather_dict["description"]}</p>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="details-grid">
                    <div class="detail-item"><p class="detail-label">Feels Like</p><p class="detail-value">{weather_dict['feels_like']:.0f}{temp_symbol}</p></div>
                    <div class="detail-item"><p class="detail-label">Humidity</p><p class="detail-value">{weather_dict['humidity']}%</p></div>
                    <div class="detail-item"><p class="detail-label">Wind</p><p class="detail-value">{weather_dict['wind_speed']:.1f} {"km/h" if unit=="Celsius" else "mph"}</p></div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Could not retrieve weather data. Please try again.")
    else:
        st.warning("City not found. Please enter a valid city name.")
elif submitted and not city:
    st.warning("Please enter a city name.")
else:
    st.info("Enter a city and click Search to see the current weather.")

