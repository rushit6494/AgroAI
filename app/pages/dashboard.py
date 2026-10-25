import streamlit as st
from app.services.history_service import (
    get_or_create_user, get_user_farms, create_farm, get_farm_history,
)

st.title("👨‍🌾 Farmer Dashboard")

if "user_id" not in st.session_state:
    st.subheader("Login / Register")
    with st.form("login_form"):
        name = st.text_input("Your name")
        phone = st.text_input("Phone number (optional, used to recognize you next time)")
        location = st.text_input("Village / District (optional)")
        submitted = st.form_submit_button("Continue")
    if submitted and name:
        uid = get_or_create_user(name, phone or None, location or None)
        st.session_state["user_id"] = uid
        st.session_state["user_name"] = name
        st.rerun()
    st.stop()

st.success(f"Welcome, {st.session_state['user_name']}! 🌾")
if st.button("Logout"):
    for k in ("user_id", "user_name", "farm_id", "farm_name"):
        st.session_state.pop(k, None)
    st.rerun()

farms = get_user_farms(st.session_state["user_id"])
farm_names = {f["farm_name"]: f["id"] for f in farms}

st.subheader("Your Farms")
col1, col2 = st.columns([2, 1])
with col1:
    if farm_names:
        selected = st.selectbox("Select a farm", list(farm_names.keys()))
        st.session_state["farm_id"] = farm_names[selected]
        st.session_state["farm_name"] = selected
    else:
        st.info("No farms yet. Add one below.")

with col2:
    with st.popover("➕ Add Farm"):
        fname = st.text_input("Farm name", key="new_farm_name")
        floc = st.text_input("Location", key="new_farm_loc")
        farea = st.number_input("Area (acres)", 0.0, 1000.0, 1.0, key="new_farm_area")
        fsoil = st.selectbox("Soil type", ["", "Black (Cotton)", "Sandy", "Loamy", "Clay", "Red", "Alluvial"], key="new_farm_soil")
        if st.button("Save Farm"):
            if fname:
                create_farm(st.session_state["user_id"], fname, floc or None, farea, fsoil or None)
                st.rerun()

if st.session_state.get("farm_id"):
    st.subheader(f"📊 Recent Activity — {st.session_state['farm_name']}")
    history = get_farm_history(st.session_state["farm_id"])
    if not history:
        st.write("No records yet. Analyze a plant or soil sample and save it here.")
    else:
        for h in history:
            with st.container(border=True):
                st.write(f"**{h['record_type'].replace('_', ' ').title()}** — {h['created_at']}")
                if h["record_type"] == "plant_analysis":
                    st.write(f"Prediction: {h['predicted_class']} ({h['confidence']}%) — Severity: {h['severity']}")
                elif h["record_type"] == "soil_analysis":
                    st.write(f"N: {h['n_value']}, P: {h['p_value']}, K: {h['k_value']}, pH: {h['ph_value']}")
                elif h["record_type"] == "crop_recommendation":
                    st.write(f"Recommended crop: {h['crop']}")
                if h["summary"]:
                    st.caption(h["summary"])