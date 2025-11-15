import streamlit as st
import requests

# ----------------- CONFIG --------------------
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Knowledge Assistant", page_icon="🧠", layout="centered")

# ----------------- SESSION STATE INIT --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER --------------------
st.title("🧠 AI Knowledge Assistant")
st.caption("Chat with your company documents")

# ----------------- PDF UPLOAD SECTION --------------------
st.subheader("📄 Upload and Process PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing document... please wait ⏳"):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{BACKEND_URL}/upload/", files=files)

    if response.status_code == 200:
        st.success("Document processed successfully! 🎉")
    else:
        st.error(f"Error: {response.text}")

st.write("---")

# ----------------- CHAT SECTION --------------------
st.subheader("💬 Ask a Question")

user_query = st.text_input("Enter your question here:")

if st.button("Ask"):
    if not user_query.strip():
        st.warning("Please enter a valid question.")
    else:
        # Save user message
        st.session_state.messages.append(("user", user_query))

        with st.spinner("Thinking... 🤔"):
            response = requests.post(
                f"{BACKEND_URL}/ask/",
                json={"question": user_query}
            )

        if response.status_code == 200:
            answer = response.json()["answer"]
            st.session_state.messages.append(("assistant", answer))
        else:
            st.error("Error contacting backend.")

# ----------------- DISPLAY CHAT HISTORY --------------------
st.write("---")
st.subheader("Conversation")

for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Assistant:** {msg}")
