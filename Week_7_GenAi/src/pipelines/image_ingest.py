import os
import json
import uuid
import fitz
import pytesseract
from PIL import Image
from pathlib import Path
from tqdm import tqdm
from transformers import BlipProcessor, BlipForConditionalGeneration
from src.config.settings import RAW_DATA_PATH, IMAGE_DIR, IMAGE_METADATA_PATH
from src.utils.logger import logger

def extract_images_from_pdf(pdf_path, image_dir):
    extracted = []
    doc = fitz.open(pdf_path)

    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            image_id = str(uuid.uuid4())
            image_name = f"{image_id}.{ext}"
            image_path = os.path.join(image_dir, image_name)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            extracted.append({
                "image_id": image_id,
                "image_path": image_path,
                "source": os.path.basename(pdf_path),
                "page": page_index + 1
            })

    doc.close()
    return extracted

def generate_caption(image_path, processor, model):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

def run_ocr(image_path):
    image = Image.open(image_path).convert("RGB")
    text = pytesseract.image_to_string(image)
    return text.strip()

def ingest_images():
    logger.info("Starting Image Ingestion Pipeline")

    Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

    pdf_files = list(Path(RAW_DATA_PATH).glob("*.pdf"))

    if not pdf_files:
        logger.error("No PDFs found in raw folder")
        return

    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    all_metadata = []

    for pdf in tqdm(pdf_files, desc="Processing PDFs"):
        logger.info(f"Extracting images from {pdf.name}")

        images = extract_images_from_pdf(str(pdf), IMAGE_DIR)

        for item in images:
            try:
                ocr_text = run_ocr(item["image_path"])
                caption = generate_caption(item["image_path"], processor, model)

                metadata = {
                    "image_id": item["image_id"],
                    "image_path": item["image_path"],
                    "source": item["source"],
                    "page": item["page"],
                    "ocr_text": ocr_text,
                    "caption": caption
                }

                all_metadata.append(metadata)

            except Exception as e:
                logger.error(f"Failed processing {item['image_path']}: {e}")

    with open(IMAGE_METADATA_PATH, "w", encoding="utf-8") as f:
        for record in all_metadata:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info(f"Saved image metadata to {IMAGE_METADATA_PATH}")

if __name__ == "__main__":
    ingest_images()
