import requests
import streamlit as st

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@st.cache_data(ttl=1800)  # 30 minute cache, farmer vaarafar request na kare
def get_weather(location_name: str):
    """Location naam (jem ke 'Rajkot, Gujarat') thi current + forecast weather aape."""
    geo = requests.get(GEOCODE_URL, params={"name": location_name, "count": 1}, timeout=10).json()
    if not geo.get("results"):
        return None

    place = geo["results"][0]
    lat, lon = place["latitude"], place["longitude"]

    resp = requests.get(WEATHER_URL, params={
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "forecast_days": 5,
        "timezone": "auto",
    }, timeout=10).json()

    return {
        "place_name": f"{place['name']}, {place.get('admin1', '')}",
        "current_temp": resp["current"]["temperature_2m"],
        "current_humidity": resp["current"]["relative_humidity_2m"],
        "current_rain": resp["current"]["precipitation"],
        "daily_dates": resp["daily"]["time"],
        "daily_rain": resp["daily"]["precipitation_sum"],
        "daily_max": resp["daily"]["temperature_2m_max"],
        "daily_min": resp["daily"]["temperature_2m_min"],
    }


def disease_risk_note(humidity: float, recent_rain: float):
    """Fakt risk context aape, confirmed diagnosis nahi."""
    if humidity >= 80 and recent_rain > 0:
        return (
            "⚠️ High humidity and recent rainfall can increase the risk of "
            "fungal/bacterial diseases. This is a general risk indicator, "
            "not a diagnosis — monitor your crop closely."
        )
    elif humidity >= 85:
        return "ℹ️ High humidity levels — monitor for early signs of fungal disease."
    return None