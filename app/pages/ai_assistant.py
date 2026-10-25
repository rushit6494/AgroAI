import streamlit as st
from app.services.assistant_service import build_response
from app.services.history_service import get_farm_history

st.title("🤖 Farmer AI Assistant")
st.caption(
    "Tamari crop ni samasya English, Hindi, ke Gujarati ma lakho "
    "(jem ke 'mara cotton ma boll ochha aave che'). Aa assistant "
    "structured guidance aape che, chatbot free-form salah nathi aapto."
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, text in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(text)

user_msg = st.chat_input("Tamari samasya lakho...")

if user_msg:
    st.session_state["chat_history"].append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

    farm_context = None
    if "farm_id" in st.session_state:
        history = get_farm_history(st.session_state["farm_id"], limit=1)
        plant_records = [h for h in history if h["record_type"] == "plant_analysis"]
        if plant_records:
            farm_context = {"last_plant_analysis": plant_records[0]}

    response = build_response(user_msg, farm_context)
    st.session_state["chat_history"].append(("assistant", response))
    with st.chat_message("assistant"):
        st.markdown(response)

if not st.session_state["chat_history"]:
    st.info(
        "Example questions: 'My cotton leaves are curling', "
        "'boll production is low', 'leaves turning yellow'"
    )