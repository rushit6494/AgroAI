import streamlit as st

st.set_page_config(page_title="AgroAI", page_icon="🌾", layout="wide")

pg = st.navigation([
    st.Page("app/pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("app/pages/crop_recommendation.py", title="Crop Recommendation", icon="🌾"),
])
pg.run()