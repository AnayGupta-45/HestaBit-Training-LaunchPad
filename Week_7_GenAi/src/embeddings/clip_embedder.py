import json
import faiss
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import torch
import clip
from sentence_transformers import SentenceTransformer

METADATA = Path("src/data/clip_metadata.jsonl")
IMAGE_INDEX = Path("src/vectorstore/image.faiss")
TEXT_INDEX = Path("src/vectorstore/text.faiss")
OCR_INDEX = Path("src/vectorstore/ocr.faiss")


def load_records():
    records = []
    with open(METADATA, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def build():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()

    text_model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    records = load_records()

    image_vecs = []
    caption_vecs = []
    ocr_vecs = []

    for rec in tqdm(records):

        try:
            img = preprocess(Image.open(rec["image_path"]).convert("RGB")).unsqueeze(0).to(device)

            with torch.no_grad():
                img_emb = model.encode_image(img).cpu().numpy().astype("float32")

            faiss.normalize_L2(img_emb)
            image_vecs.append(img_emb[0])

            tokens = clip.tokenize([rec["caption"]]).to(device)
            with torch.no_grad():
                txt_emb = model.encode_text(tokens).cpu().numpy().astype("float32")

            faiss.normalize_L2(txt_emb)
            caption_vecs.append(txt_emb[0])

            ocr_text = rec["ocr_text"].strip()
            if len(ocr_text) < 5:
                ocr_text = rec["caption"]

            ocr_emb = text_model.encode([ocr_text], normalize_embeddings=True)
            ocr_vecs.append(ocr_emb[0].astype("float32"))

        except:
            continue

    image_vecs = np.array(image_vecs).astype("float32")
    caption_vecs = np.array(caption_vecs).astype("float32")
    ocr_vecs = np.array(ocr_vecs).astype("float32")

    img_index = faiss.IndexFlatIP(image_vecs.shape[1])
    img_index.add(image_vecs)
    faiss.write_index(img_index, str(IMAGE_INDEX))

    txt_index = faiss.IndexFlatIP(caption_vecs.shape[1])
    txt_index.add(caption_vecs)
    faiss.write_index(txt_index, str(TEXT_INDEX))

    ocr_index = faiss.IndexFlatIP(ocr_vecs.shape[1])
    ocr_index.add(ocr_vecs)
    faiss.write_index(ocr_index, str(OCR_INDEX))


if __name__ == "__main__":
    build()
