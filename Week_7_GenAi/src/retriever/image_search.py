import json
import faiss
import torch
import clip
from PIL import Image
from pathlib import Path
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import BlipProcessor, BlipForConditionalGeneration

IMAGE_INDEX = Path("src/vectorstore/image.faiss")
TEXT_INDEX = Path("src/vectorstore/text.faiss")
OCR_INDEX = Path("src/vectorstore/ocr.faiss")
METADATA = Path("src/data/clip_metadata.jsonl")


class ImageSearch:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        self.image_index = faiss.read_index(str(IMAGE_INDEX))
        self.text_index = faiss.read_index(str(TEXT_INDEX))
        self.ocr_index = faiss.read_index(str(OCR_INDEX))

        self.records = []
        with open(METADATA, "r", encoding="utf-8") as f:
            for line in f:
                self.records.append(json.loads(line))

        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.text_model = SentenceTransformer("BAAI/bge-base-en-v1.5")

        self.caption_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            local_files_only=True
        )

        self.caption_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            local_files_only=True
        ).to(self.device)

        self.caption_model.eval()

    def normalize(self, vec):
        faiss.normalize_L2(vec)
        return vec

    def caption_query_image(self, path):
        image = Image.open(path).convert("RGB")
        inputs = self.caption_processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            out = self.caption_model.generate(**inputs)

        caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
        return caption

    def text_to_image(self, query, k=5):
        tokens = clip.tokenize([query]).to(self.device)

        with torch.no_grad():
            emb = self.model.encode_text(tokens).cpu().numpy().astype("float32")

        emb = self.normalize(emb)

        scores, idx = self.image_index.search(emb, k)

        return [self.records[i] for i in idx[0] if i != -1]

    def image_to_image(self, path, k=5):
        img = self.preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            emb = self.model.encode_image(img).cpu().numpy().astype("float32")

        emb = self.normalize(emb)

        scores, idx = self.image_index.search(emb, k)

        return [self.records[i] for i in idx[0] if i != -1]

    def image_to_text(self, path, k=5):

        query_caption = self.caption_query_image(path)

        img = self.preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            img_emb = self.model.encode_image(img).cpu().numpy().astype("float32")

        img_emb = self.normalize(img_emb)

        scores_img, idx_img = self.text_index.search(img_emb, 5)

        ocr_query_emb = self.text_model.encode(
            [query_caption], normalize_embeddings=True
        ).astype("float32")

        scores_ocr, idx_ocr = self.ocr_index.search(ocr_query_emb, 5)

        combined_ids = list(set(idx_img[0]) | set(idx_ocr[0]))
        candidates = [self.records[i] for i in combined_ids if i != -1]

        pairs = []
        for c in candidates:
            text = (c["caption"] or "") + " " + (c["ocr_text"] or "")
            pairs.append([query_caption, text])

        rerank_scores = self.reranker.predict(pairs)

        ranked = sorted(zip(candidates, rerank_scores), key=lambda x: x[1], reverse=True)

        return [r[0]["retrieval_text"] for r in ranked[:k]]


if __name__ == "__main__":
    search = ImageSearch()

    while True:
        mode = input("\n1 Text→Image | 2 Image→Image | 3 Image→Text | q Quit : ")

        if mode == "1":
            q = input("Enter query: ")
            res = search.text_to_image(q)
            print(json.dumps(res, indent=2))

        elif mode == "2":
            p = input("Enter image path: ")
            res = search.image_to_image(p)
            print(json.dumps(res, indent=2))

        elif mode == "3":
            p = input("Enter image path: ")
            res = search.image_to_text(p)
            print("\n".join(res))

        elif mode == "q":
            break