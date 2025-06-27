import streamlit as st
import requests

st.set_page_config(page_title="LLM Q&A App", page_icon="🧠")

st.title("🧠 LLM-Powered PDF Q&A")

st.sidebar.title("Settings")
backend_url = st.sidebar.text_input("Backend URL", "http://localhost:8000")

st.sidebar.subheader("OpenAI API Key")
openai_key = st.sidebar.text_input(
    "Enter your OpenAI API Key (optional):", type="password"
)

st.sidebar.subheader("Choose LLM Model")
model = st.sidebar.selectbox("Model", ["openai", "huggingface", "ollama"])

st.subheader("Upload a PDF")
pdf_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if pdf_file is not None:
    with st.spinner("Uploading and processing PDF..."):
        files = {"file": (pdf_file.name, pdf_file, "application/pdf")}
        try:
            res = requests.post(f"{backend_url}/upload", files=files)
            if res.status_code == 200:
                st.success("✅ PDF uploaded and processed successfully!")
            else:
                st.error(f"❌ Upload failed: {res.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.subheader("Ask a Question")
question = st.text_input("Enter your question about the PDF")

if st.button("Get Answer"):
    if not question:
        st.warning("⚠️ Please enter a question.")
    else:
        payload = {
            "question": question,
            "model": model,
            "openai_api_key": openai_key if openai_key else None
        }
        try:
            with st.spinner("Getting answer..."):
                res = requests.post(f"{backend_url}/query", json=payload)
                if res.status_code == 200:
                    result = res.json()
                    if 'answer' in result:
                        st.success(f"Answer: {result['answer']}")
                    else:
                        st.error(f"❌ Error: {result.get('error')}")
                else:
                    st.error(f"❌ Query failed: {res.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

