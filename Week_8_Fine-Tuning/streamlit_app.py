import streamlit as st
import requests
import uuid
import time

st.set_page_config(page_title="TinyLlama Local LLM", layout="wide")

API_SINGLE = "http://127.0.0.1:8000/generate/stream"
API_CHAT = "http://127.0.0.1:8000/chat/stream"

st.title("Test Model")

mode = st.radio("Mode", ["Single Prompt", "Chat Mode"], horizontal=True)

st.sidebar.header("Settings")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="You are a strict coding assistant. Only answer programming-related questions. If insufficient information, say you don't know."
)

temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.3, 0.05)
top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 0.9, 0.05)
top_k = st.sidebar.slider("Top-k", 1, 100, 40)
max_tokens = st.sidebar.slider("Max Tokens", 1, 1024, 256)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if mode == "Single Prompt":

    prompt = st.chat_input("Type your prompt and press Enter...")

    if prompt:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        start_time = time.time()

        response = requests.post(
            API_SINGLE,
            json={
                "system_prompt": system_prompt,
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_tokens": max_tokens
            },
            stream=True
        )

        full_response = ""

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()

            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    token = chunk.decode("utf-8")
                    full_response += token
                    placeholder.markdown(full_response)

        end_time = time.time()
        latency = end_time - start_time
        tokens = len(full_response.split())
        tps = tokens / latency if latency > 0 else 0

        st.caption(f"{latency:.2f}s | {tokens} tokens | {tps:.2f} tok/sec")

else:

    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message and press Enter...")

    if user_input:

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)

        start_time = time.time()

        response = requests.post(
            API_CHAT,
            json={
                "session_id": st.session_state.session_id,
                "system_prompt": system_prompt,
                "message": user_input,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_tokens": max_tokens
            },
            stream=True
        )

        full_response = ""

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()

            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    token = chunk.decode("utf-8")
                    full_response += token
                    placeholder.markdown(full_response)

        end_time = time.time()

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        latency = end_time - start_time
        tokens = len(full_response.split())
        tps = tokens / latency if latency > 0 else 0

        st.caption(f"{latency:.2f}s | {tokens} tokens | {tps:.2f} tok/sec")