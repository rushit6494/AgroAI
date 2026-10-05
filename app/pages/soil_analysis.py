import streamlit as st
from ml.soil_analysis.rules import analyze_soil

st.title("🧪 Soil Analysis")
st.caption("Soil nutrient ane pH details bharo. Aa general guidance aape che, certified soil test no vikalp nathi.")

with st.form("soil_form"):
    c1, c2 = st.columns(2)
    with c1:
        n = st.number_input("Nitrogen (N)", 0.0, 200.0, 50.0)
        p = st.number_input("Phosphorus (P)", 0.0, 200.0, 50.0)
        k = st.number_input("Potassium (K)", 0.0, 250.0, 50.0)
    with c2:
        ph = st.number_input("Soil pH", 0.0, 14.0, 6.5, step=0.1)
        moisture = st.number_input("Soil Moisture (%, optional)", 0.0, 100.0, 0.0)
        soil_type = st.selectbox("Soil Type (optional)", ["", "Sandy", "Loamy", "Clay", "Black (Cotton)", "Red", "Alluvial"])
    submitted = st.form_submit_button("🔍 Analyze Soil", use_container_width=True)

if submitted:
    result = analyze_soil(n, p, k, ph, moisture or None, soil_type or None)

    st.subheader("Nutrient Status")
    cols = st.columns(3)
    colors = {"Low": "🔴", "Medium": "🟡", "High": "🟢"}
    for col, (nutrient, level) in zip(cols, result["nutrient_status"].items()):
        col.metric(nutrient, f"{colors[level]} {level}")

    st.subheader("pH Interpretation")
    st.write(f"**{result['ph_label']}** — {result['ph_note']}")

    st.subheader("Summary")
    st.info(result["summary"])

    st.caption(
        "⚠️ These thresholds are derived from general crop-recommendation data, "
        "not a certified soil-testing standard. For precise nutrient management, "
        "get a certified soil test and consult a local agricultural expert."
    )