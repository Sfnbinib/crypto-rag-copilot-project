import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("Crypto RAG Copilot Demo")

question = st.text_input("Ask a question about crypto docs:")

if st.button("Ask"):
    if question:
        try:
            resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=30)
            data = resp.json()
            st.subheader("Answer")
            st.write(data.get("answer", "No answer"))
            st.subheader("Citations")
            citations = data.get("citations", [])
            for c in citations:
                st.write(f"- {c['source']} (offset {c['offset']})")
            st.write(f"Latency: {data.get('latency_ms', 0)} ms")
        except Exception as e:
            st.error(f"Error: {e}")
