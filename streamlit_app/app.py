import requests
import streamlit as st
import uuid

st.set_page_config(page_title="Financial Assistant", page_icon="💼", layout="centered")

API_URL = "http://fastapi:80/api/agent"

st.title("💼 Financial Assistant")
st.caption("Your financial document analysis assistant")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Generate unique thread_id for each user session (only once per session)
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"

# Display thread_id in sidebar for debugging (optional)
with st.sidebar:
    st.caption(f"Session ID: `{st.session_state.thread_id}`")

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.write(text)

msg = st.chat_input("Write your message...")

if msg:
    st.session_state.history.append(("user", msg))
    with st.chat_message("user"):
        st.write(msg)

    try:
        payload = {"question": msg, "thread_id": st.session_state.thread_id}

        r = requests.post(API_URL, json=payload)
        answer = r.json().get("answer", "no answer")
    except Exception as e:
        answer = f"Error: {e}"

    st.session_state.history.append(("assistant", answer))
    with st.chat_message("assistant"):
        st.write(answer)
