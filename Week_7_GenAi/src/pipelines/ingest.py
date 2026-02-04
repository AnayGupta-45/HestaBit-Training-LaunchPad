import json
import uuid
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.text_cleaner import clean_text
from src.utils.logger import logger
from src.config.settings import RAW_DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP, CHUNKS_PATH

def load_documents():
    logger.info("Loading PDF documents")

    loader = DirectoryLoader(
        path=RAW_DATA_PATH,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    docs = loader.load()
    logger.info(f"PDF pages loaded: {len(docs)}")
    return docs

def chunk_documents(docs):
    logger.info("Cleaning and chunking PDF text")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []

    for doc in docs:
        cleaned_text = clean_text(doc.page_content)

        if not cleaned_text.strip():
            continue

        chunks = splitter.split_text(cleaned_text)

        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk,
                "metadata": {
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "chunk_index": idx
                }
            })

    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks

def save_chunks(chunks):
    Path(CHUNKS_PATH).parent.mkdir(parents=True, exist_ok=True)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    logger.info(f"Chunks saved at {CHUNKS_PATH}")

def main():
    logger.info("STEP 1 STARTED: PDF ingestion + chunking")

    docs = load_documents()
    chunks = chunk_documents(docs)
    save_chunks(chunks)

    logger.info("STEP 1 COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
