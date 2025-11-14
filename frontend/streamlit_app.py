import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# CONFIGURATION
BACKEND_URL = "http://127.0.0.1:8000" 
st.set_page_config(page_title="AI Knowledge Assistant", page_icon="🧠")

#session state initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def upload_pdf_to_backend(file):
    """Send PDF file to FastAPI backend."""
    upload_url = f"{BACKEND_URL}/upload/"
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(upload_url, files=files)
    return response.json()
def ask_question_to_backend(question):
    """Send question to FastAPI backend and get the answer."""
    ask_url = f"{BACKEND_URL}/ask/"
    payload = {"question": question}
    response = requests.post(ask_url,json = {"question": question})
    return response.json()


# UI COMPONENTS
st.title("🧠 AI Knowledge Assistant")
st.write("Chat with your company documents")

st.divider()

st.header("📄 Upload and Process PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Uploading and processing PDF..."):
        result = upload_pdf_to_backend(uploaded_file)
    if "success" in result.get("status", ""):
            st.success("Document processed successfully! 🎉")
    else:
        st.error(f"Error: {result.get('detail', 'Unknown error')}")

st.divider()

st.header("💬 Ask a Question")
question = st.text_input("Enter your question here:")

if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a valid question.")
    else:
        with st.spinner("Getting answer..."):
            response = ask_question_to_backend(question)
        answer = response.get("answer", "No answer found.")
        
        st.session_state.chat_history.append(("user", question))
        st.session_state.chat_history.append(("assistant", answer))

# Display chat history

for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Assistant:** {message}")