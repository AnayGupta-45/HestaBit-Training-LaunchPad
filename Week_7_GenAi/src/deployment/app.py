import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.pipelines.main_pipeline import EnterpriseAssistant


@st.cache_resource
def load_assistant():
    return EnterpriseAssistant()


assistant = load_assistant()

st.set_page_config(page_title="Enterprise Knowledge Assistant", layout="centered")

st.title("Enterprise Knowledge Assistant")


mode = st.sidebar.selectbox("Select Mode", ["Text RAG", "Image RAG", "SQL QA"])

if st.sidebar.button("Clear Memory"):
    assistant.memory.clear()
    st.sidebar.success("Memory cleared")


if mode == "Text RAG":
    query = st.text_input("Enter your question")

    if st.button("Ask") and query:
        with st.spinner("Processing..."):
            result = assistant.handle_text(query)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Confidence Score")
        st.write(f"{result['confidence']}%")

        st.subheader("Faithfulness Score")
        st.write(result["faithfulness"])

        st.subheader("Hallucination Detected")
        st.write("Yes" if result["hallucination"] else "No")

        st.subheader("Sources")
        st.json(result["sources"])


elif mode == "Image RAG":
    sub_mode = st.selectbox(
        "Select Image Mode", ["text_to_image", "image_to_image", "image_to_text"]
    )

    if sub_mode == "text_to_image":
        query = st.text_input("Enter your query")

        if st.button("Search") and query:
            with st.spinner("Searching images..."):
                result = assistant.handle_image(sub_mode, query=query)

            st.subheader("Retrieved Images")

            for img_path in result.get("images", []):
                st.image(str(Path(img_path).resolve()), use_column_width=True)

            st.subheader("Confidence Score")
            st.write(f"{result['confidence']}%")

            st.subheader("Faithfulness Score")
            st.write(result["faithfulness"])

            st.subheader("Hallucination Detected")
            st.write("Yes" if result["hallucination"] else "No")

    elif sub_mode == "image_to_image":
        uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

        if uploaded:
            temp_path = Path("temp_image.jpg")

            with open(temp_path, "wb") as f:
                f.write(uploaded.read())

            if st.button("Search Similar"):
                with st.spinner("Finding similar images..."):
                    result = assistant.handle_image(sub_mode, image_path=str(temp_path))

                st.subheader("Retrieved Images")

                for img_path in result.get("images", []):
                    st.image(str(Path(img_path).resolve()), use_column_width=True)

                st.subheader("Confidence Score")
                st.write(f"{result['confidence']}%")

                st.subheader("Faithfulness Score")
                st.write(result["faithfulness"])

                st.subheader("Hallucination Detected")
                st.write("Yes" if result["hallucination"] else "No")

    elif sub_mode == "image_to_text":
        uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

        if uploaded:
            temp_path = Path("temp_image.jpg")

            with open(temp_path, "wb") as f:
                f.write(uploaded.read())

            if st.button("Generate Caption"):
                with st.spinner("Generating caption..."):
                    result = assistant.handle_image(sub_mode, image_path=str(temp_path))

                st.subheader("Generated Caption")
                st.write(result["answer"])

                st.subheader("Confidence Score")
                st.write(f"{result['confidence']}%")

                st.subheader("Faithfulness Score")
                st.write(result["faithfulness"])

                st.subheader("Hallucination Detected")
                st.write("Yes" if result["hallucination"] else "No")

elif mode == "SQL QA":
    query = st.text_input("Enter SQL question")

    if st.button("Ask") and query:
        with st.spinner("Running SQL pipeline..."):
            result = assistant.handle_sql(query)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Confidence Score")
        st.write(f"{result['confidence']}%")

        st.subheader("Faithfulness Score")
        st.write(result["faithfulness"])

        st.subheader("Hallucination Detected")
        st.write("Yes" if result["hallucination"] else "No")
