import streamlit as st

st.set_page_config(page_title="AgroAI", page_icon="🌾", layout="wide")

pg = st.navigation([
    st.Page("app/pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("app/pages/dashboard.py", title="Dashboard", icon="👨‍🌾"),
    st.Page("app/pages/ai_assistant.py", title="AI Assistant", icon="🤖"),
    st.Page("app/pages/crop_recommendation.py", title="Crop Recommendation", icon="🌾"),
    st.Page("app/pages/plant_analysis.py", title="Plant Analysis", icon="📸"),
    st.Page("app/pages/soil_analysis.py", title="Soil Analysis", icon="🧪"),
])
pg.run()