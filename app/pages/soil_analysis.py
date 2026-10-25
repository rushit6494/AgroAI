import streamlit as st
from ml.soil_analysis.rules import analyze_soil
from app.services.history_service import save_record

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
    st.session_state["last_soil_result"] = result
    st.session_state["last_soil_inputs"] = {"n": n, "p": p, "k": k, "ph": ph}

if "last_soil_result" in st.session_state:
    result = st.session_state["last_soil_result"]
    inputs = st.session_state["last_soil_inputs"]

    st.subheader("Nutrient Status")
    cols = st.columns(3)
    colors = {"Low": "🔴", "Medium": "🟡", "High": "🟢"}
    for col, (nutrient, level) in zip(cols, result["nutrient_status"].items()):
        col.metric(nutrient, f"{colors[level]} {level}")

    st.subheader("pH Interpretation")
    st.write(f"**{result['ph_label']}** — {result['ph_note']}")

    st.subheader("Summary")
    st.info(result["summary"])

    if "farm_id" in st.session_state:
        if st.button("💾 Save to History"):
            save_record(
                farm_id=st.session_state["farm_id"],
                record_type="soil_analysis",
                n_value=inputs["n"], p_value=inputs["p"],
                k_value=inputs["k"], ph_value=inputs["ph"],
                summary=result["summary"],
            )
            st.success("Saved to your farm history!")
    else:
        st.caption("ℹ️ Log in on the Dashboard page and select a farm to save this result.")

    st.caption(
        "⚠️ These thresholds are derived from general crop-recommendation data, "
        "not a certified soil-testing standard. For precise nutrient management, "
        "get a certified soil test and consult a local agricultural expert."
    )