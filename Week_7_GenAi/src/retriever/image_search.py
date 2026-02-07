import json
import faiss
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from src.config.settings import (
    IMAGE_INDEX_FILE,
    IMAGE_METADATA_STORE,
    TOP_K_VECTOR
)
from src.utils.logger import logger

class ImageSearch:

    def __init__(self):
        logger.info("Initializing Image Search System")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        self.model.to(self.device)
        self.model.eval()

        self.index = faiss.read_index(IMAGE_INDEX_FILE)

        with open(IMAGE_METADATA_STORE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search_by_text(self, query, top_k=TOP_K_VECTOR):
        logger.info(f"Text → Image search: {query}")

        inputs = self.processor(text=[query], return_tensors="pt", padding=True).to(self.device)

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)

        # Fix for BaseModelOutputWithPooling error
        if hasattr(text_features, "pooler_output"):
            text_features = text_features.pooler_output
        elif not isinstance(text_features, torch.Tensor):
            text_features = text_features[0]

        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        query_vector = text_features.cpu().numpy().astype("float32")

        scores, indices = self.index.search(query_vector, top_k)
        
        results = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
        return results

    def search_by_image(self, image_path, top_k=TOP_K_VECTOR):
        logger.info(f"Image → Image search: {image_path}")

        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)

        # Fix for BaseModelOutputWithPooling error
        if hasattr(image_features, "pooler_output"):
            image_features = image_features.pooler_output
        elif not isinstance(image_features, torch.Tensor):
            image_features = image_features[0]

        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        query_vector = image_features.cpu().numpy().astype("float32")

        scores, indices = self.index.search(query_vector, top_k)
        
        results = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
        return results

    def image_to_text_context(self, image_path, top_k=TOP_K_VECTOR):
        results = self.search_by_image(image_path, top_k)

        combined_text = ""
        for item in results:
            combined_text += f"\nCaption: {item.get('caption', '')}\n"
            combined_text += f"OCR: {item.get('ocr_text', '')}\n"

        return combined_text

if __name__ == "__main__":
    search = ImageSearch()

    while True:
        mode = input("Mode (1=text, 2=image, 3=image→text, q=quit): ")

        if mode == "1":
            query = input("Enter text query: ")
            results = search.search_by_text(query)
            print(json.dumps(results, indent=2))

        elif mode == "2":
            path = input("Enter image path: ")
            results = search.search_by_image(path)
            print(json.dumps(results, indent=2))

        elif mode == "3":
            path = input("Enter image path: ")
            context = search.image_to_text_context(path)
            print(context)

        elif mode == "q":
            break