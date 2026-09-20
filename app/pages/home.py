import streamlit as st
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

st.title("🌾 AgroAI – Smart Crop & Plant Health Assistant")
st.subheader("AI-Powered Smart Farming Assistant")
st.write("Analyze your crops, understand plant health, and make data-informed farming decisions.")

try:
    with create_engine(DATABASE_URL).connect() as conn:
        conn.execute(text("SELECT 1"))
    st.success("MySQL connected ✅")
except Exception as e:
    st.error(f"MySQL connection failed: {e}")