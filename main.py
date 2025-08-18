import streamlit as st
import requests
from pathlib import Path
from utils.api_utils import get_weather_from_city
from config.py import API_KEY

st.title('Weather API')

city = st.text_input('Enter a city name: ', placeholder='Enter the city that you want to check the weather of!')


with st.sidebar:
    unit = st.selectbox(
        "Temperature unit:",
        options=["Celsius", "Fahrenheit"]
    )
    st.write(f"Selected unit: {unit}")

metric_dict = {
    "Celsius": "metric",
    "Fahrenheit": "imperial",
}
metric = metric_dict.get(unit)

try: 
    weather_dict = get_weather_from_city(city=city, api_key=api_key, metric=metric)
    with st.expander("🌡️ Temperature Info"):
        st.write(f"Current: {weather_dict['temp']}°")
        st.write(f"Feels like: {weather_dict['feels_like']}°")
        st.write(f"Min Temp: {weather_dict['temp_min']}°")
        st.write(f"Max Temp: {weather_dict['temp_max']}°")

    with st.expander("💨 Atmospheric Conditions"):
        st.write(f"Humidity: {weather_dict['humidity']}%")
        st.write(f"Pressure: {weather_dict['pressure']} hPa")
except KeyError: 
    st.write("Please choose a city... ")




