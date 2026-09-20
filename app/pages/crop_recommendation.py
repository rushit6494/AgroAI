import streamlit as st
from ml.crop_recommendation.predict import predict_crops

st.title("🌾 Crop Recommendation")
st.caption("Soil ane weather ni details bharo. Model suitable crops ni ranking aapse.")

with st.form("crop_form"):
    c1, c2 = st.columns(2)
    with c1:
        N = st.number_input("Nitrogen (N)", 0.0, 140.0, 90.0)
        P = st.number_input("Phosphorus (P)", 5.0, 145.0, 42.0)
        K = st.number_input("Potassium (K)", 5.0, 205.0, 43.0)
        ph = st.number_input("Soil pH", 3.5, 9.9, 6.5, step=0.1)
    with c2:
        temperature = st.number_input("Temperature (°C)", 8.0, 44.0, 25.5, step=0.5)
        humidity = st.number_input("Humidity (%)", 14.0, 100.0, 80.0)
        rainfall = st.number_input("Rainfall (mm)", 20.0, 300.0, 200.0)
    submitted = st.form_submit_button("🔍 Recommend Crop", use_container_width=True)

if submitted:
    try:
        results = predict_crops(N, P, K, temperature, humidity, ph, rainfall, top_k=3)
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        st.stop()

    st.subheader("Recommended Crops")
    medals = ["🥇", "🥈", "🥉"]
    for r in results:
        st.markdown(f"### {medals[r['rank'] - 1]} {r['crop'].title()}")

    # Top 2 nazdik hoy to chetavani
    if results[0]["score"] - results[1]["score"] < 0.15:
        st.warning(
            f"**{results[0]['crop'].title()}** ane **{results[1]['crop'].title()}** "
            "nu model score lagbhag sarkhu che. Local agricultural expert ni salah leva."
        )

    with st.expander("Model details"):
        for r in results:
            st.write(f"{r['crop'].title()}: {r['score']:.2f}")
        st.caption(
            "Aa relative model score che (Random Forest na trees na vote), "
            "real probability nathi."
        )

    st.info(
        "Aa AI model ni suggestion che, official salah nathi. "
        "Vaavetar pehla soil test ane local agricultural expert ni salah leva."
    )