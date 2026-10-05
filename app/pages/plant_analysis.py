import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from ml.disease_detection.predict import predict_disease
from config.settings import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_MB

st.title("📸 Plant Health Analysis")
st.caption("Cotton plant/leaf no photo upload karo. Model possible disease, pest, athva damage identify karse.")

uploaded = st.file_uploader(
    "Cotton leaf/plant photo upload karo",
    type=ALLOWED_IMAGE_TYPES,
    help=f"Max {MAX_UPLOAD_MB} MB. JPG, JPEG, ane PNG supported.",
)

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

        with col2:
            st.subheader(f"Crop: {result['crop']}")

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

if result["confident"] and result["top_prediction"]["type"] in NEXT_STEPS:
    icon = {"disease": "🦠", "pest": "🐛", "physical_damage": "⚠️"}[result["top_prediction"]["type"]]
    st.markdown(f"#### {icon} Suggested Next Steps")
    st.write(NEXT_STEPS[result["top_prediction"]["type"]])

            st.caption(
                "This is an AI-generated analysis, not an official diagnosis. "
                "Always confirm with a qualified agricultural expert before taking action."
            )