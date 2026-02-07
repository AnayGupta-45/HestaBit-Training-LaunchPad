import json
import faiss
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import torch
from transformers import CLIPProcessor, CLIPModel

from src.config.settings import (
    IMAGE_METADATA_PATH,
    IMAGE_EMBEDDINGS_FILE,
    IMAGE_INDEX_FILE,
    IMAGE_METADATA_STORE
)

from src.utils.logger import logger

BATCH_SIZE = 16
MODEL_NAME = "openai/clip-vit-base-patch32"


def load_metadata():
    records = []
    with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def embed_images():
    logger.info("Starting CLIP Image Embedding Pipeline")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME)
    model.to(device)
    model.eval()

    metadata = load_metadata()

    embeddings = []
    valid_metadata = []

    for i in tqdm(range(0, len(metadata), BATCH_SIZE), desc="Embedding Images"):
        batch_records = metadata[i:i + BATCH_SIZE]

        images = []
        batch_meta = []

        for record in batch_records:
            try:
                img = Image.open(record["image_path"]).convert("RGB")
                images.append(img)
                batch_meta.append(record)
            except Exception as e:
                logger.error(f"Failed loading image {record['image_path']}: {e}")

        if not images:
            continue

        inputs = processor(images=images, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            vision_outputs = model.vision_model(**inputs)
            image_features = vision_outputs.pooler_output
            image_features = model.visual_projection(image_features)

        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

        vectors = image_features.cpu().numpy().astype("float32")

        embeddings.extend(vectors)
        valid_metadata.extend(batch_meta)

    if len(embeddings) == 0:
        logger.warning("No embeddings generated.")
        return

    embeddings = np.array(embeddings).astype("float32")

    Path(IMAGE_EMBEDDINGS_FILE).parent.mkdir(parents=True, exist_ok=True)
    np.save(IMAGE_EMBEDDINGS_FILE, embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    Path(IMAGE_INDEX_FILE).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, IMAGE_INDEX_FILE)

    with open(IMAGE_METADATA_STORE, "w", encoding="utf-8") as f:
        json.dump(valid_metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(embeddings)} image embeddings")
    logger.info("FAISS Image Index Built Successfully")


if __name__ == "__main__":
    embed_images()
