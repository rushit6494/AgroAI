import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from ml.disease_detection.predict import predict_disease
from app.services.treatment_service import get_treatment
from app.services.history_service import save_record
from app.services.report_service import generate_plant_report
from config.settings import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_MB

st.title("📸 Plant Health Analysis")
st.caption(
    "**Fakt cotton leaf/plant no saaf photo upload karo** "
    "(close-up, barabar prakash ma). Model possible disease, pest, "
    "athva damage identify karse."
)

uploaded = st.file_uploader(
    "Cotton leaf/plant photo upload karo",
    type=ALLOWED_IMAGE_TYPES,
    help=f"Max {MAX_UPLOAD_MB} MB. JPG, JPEG, ane PNG supported.",
)

NEXT_STEPS = {
    "disease": (
        "- Inspect nearby plants for similar symptoms.\n"
        "- Monitor disease spread over the next few days.\n"
        "- Avoid working in the field when leaves are wet (reduces spread).\n"
        "- Consult a local agricultural expert for confirmation before any treatment."
    ),
    "pest": (
        "- Check undersides of leaves for insects (nymphs/adults).\n"
        "- Inspect neighboring plants and field borders for insect vectors.\n"
        "- Use yellow sticky traps to monitor pest population, if available.\n"
        "- Consult a local agricultural expert before applying any pesticide."
    ),
    "physical_damage": (
        "- Check recent spray history and nearby herbicide use.\n"
        "- Avoid further chemical application until the cause is confirmed.\n"
        "- Monitor whether new growth shows the same symptoms.\n"
        "- Consult a local agricultural expert to confirm the cause."
    ),
}

if uploaded is not None:
    if uploaded.size > MAX_UPLOAD_MB * 1024 * 1024:
        st.error(f"File {MAX_UPLOAD_MB} MB thi moti che. Nani image upload karo.")
        st.stop()

    image = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns([1, 1.3])
    with col1:
        st.image(image, caption="Uploaded image", use_container_width=True)

    analyze = st.button("🔍 Analyze Plant", use_container_width=True)

    if analyze:
        with st.spinner("Analyzing..."):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                image.save(tmp.name)
                result = predict_disease(Path(tmp.name))

        st.session_state["last_plant_result"] = result

    if "last_plant_result" in st.session_state:
        result = st.session_state["last_plant_result"]

        with col2:
            st.subheader(f"Crop: {result['crop']}")

            st.caption(
                "⚠️ This model is trained only on cotton leaves. If the uploaded "
                "image is not a cotton leaf, or is blurry/unclear, this result "
                "is not reliable."
            )

            if not result["confident"]:
                st.warning(result["message"])
            elif result["top_prediction"]["type"] == "healthy":
                st.success(result["message"])
            elif result["top_prediction"]["type"] == "unknown_cause":
                st.info(result["message"])
            elif result["top_prediction"]["type"] == "pest":
                st.warning(f"🐛 {result['message']}")
            else:
                st.error(result["message"])

            st.markdown("#### Severity")
            st.write(result["severity"])

            st.markdown("#### Model predictions")
            for p in result["predictions"]:
                st.write(f"- **{p['label']}**: {p['confidence']:.0%}")

            if result["confident"] and result["top_prediction"]["type"] in NEXT_STEPS:
                icon = {"disease": "🦠", "pest": "🐛", "physical_damage": "⚠️"}[result["top_prediction"]["type"]]
                st.markdown(f"#### {icon} Suggested Next Steps")
                st.write(NEXT_STEPS[result["top_prediction"]["type"]])

            if result["confident"] and result["top_prediction"]["type"] in ("disease", "pest"):
                treatments = get_treatment(result["top_prediction"]["class"])
                st.markdown("#### 💊 Treatment Information")
                if not treatments:
                    st.write("No verified treatment record found in the database for this issue yet.")
                else:
                    for t in treatments:
                        verified_badge = "✅ Verified" if t["is_verified"] else "⚠️ NOT VERIFIED — demo data only"
                        with st.container(border=True):
                            st.markdown(f"**{t['product_name']}** &nbsp; `{verified_badge}`")
                            st.write(f"Active ingredient: {t['active_ingredient']} ({t['formulation']})")
                            st.write(f"Purpose: {t['purpose']}")
                            st.write(f"Application: {t['application_method']}")
                            st.write(f"Rate: {t['application_rate']}  |  Dilution: {t['water_dilution']}")
                            st.write(f"Safety: {t['safety_instructions']}")
                            if not t["is_verified"]:
                                st.error(
                                    "This record is placeholder/demo data for development only. "
                                    "Do NOT use this for actual application. Always follow the "
                                    "real product label and consult a certified agricultural expert."
                                )

            if "farm_id" in st.session_state:
                if st.button("💾 Save to History"):
                    save_record(
                        farm_id=st.session_state["farm_id"],
                        record_type="plant_analysis",
                        crop=result["crop"],
                        predicted_class=result["top_prediction"]["label"],
                        confidence=round(result["top_prediction"]["confidence"] * 100, 2),
                        severity=result["severity"],
                        summary=result["message"],
                    )
                    st.success("Saved to your farm history!")
            else:
                st.caption("ℹ️ Log in on the Dashboard page and select a farm to save this result.")

            pdf_bytes = generate_plant_report(
                farmer_name=st.session_state.get("user_name"),
                farm_name=st.session_state.get("farm_name"),
                result=result,
            )
            st.download_button(
                "📄 Download PDF Report", data=pdf_bytes,
                file_name=f"AgroAI_Plant_Report_{result['crop']}.pdf",
                mime="application/pdf",
            )

            st.caption(
                "This is an AI-generated analysis, not an official diagnosis. "
                "Always confirm with a qualified agricultural expert before taking action."
            )