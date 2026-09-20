import streamlit as st
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

st.set_page_config(page_title="AgroAI", page_icon="🌾", layout="wide")

st.title("🌾 AgroAI – Smart Crop & Plant Health Assistant")
st.success("Phase 0 setup successful ✅")

# DB connection test
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    st.success("MySQL connected ✅")
except Exception as e:
    st.error(f"MySQL connection failed: {e}")