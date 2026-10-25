import streamlit as st
from app.services.weather_service import get_weather, disease_risk_note

st.title("🌦️ Weather")
st.caption("Tamari location no weather joi ne crop risk samjo.")

location = st.text_input("Village / District / City", placeholder="e.g. Rajkot, Gujarat")

if st.button("🔍 Get Weather", use_container_width=True) and location:
    with st.spinner("Fetching weather..."):
        data = get_weather(location)

    if data is None:
        st.error("Location not found. Try a different name (e.g. city or district name).")
    else:
        st.subheader(f"📍 {data['place_name']}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{data['current_temp']}°C")
        c2.metric("Humidity", f"{data['current_humidity']}%")
        c3.metric("Current Rain", f"{data['current_rain']} mm")

        risk = disease_risk_note(data["current_humidity"], data["current_rain"])
        if risk:
            st.warning(risk)

        st.subheader("5-Day Forecast")
        for date, rain, tmax, tmin in zip(
            data["daily_dates"], data["daily_rain"], data["daily_max"], data["daily_min"]
        ):
            st.write(f"**{date}** — 🌡️ {tmin}°C to {tmax}°C, 🌧️ {rain} mm rain")

        st.caption(
            "Weather conditions can increase disease risk but do not confirm a "
            "specific disease. Use the Plant Analysis page for symptom-based checks."
        )