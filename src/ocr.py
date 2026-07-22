import os
import json
import re
from PIL import Image
import cv2
import numpy as np
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# ── Path Setup ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")

# ── Load TrOCR Model ─────────────────────────────────────────
print("Loading TrOCR handwriting model...")
print("(First time only — downloads ~1.5GB, please wait...)")

processor = TrOCRProcessor.from_pretrained(
    "microsoft/trocr-large-handwritten"
)
model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-large-handwritten"
)
model.eval()
print("✅ TrOCR model loaded!")


def preprocess_image(image_path):
    """
    Cleans the image before OCR for better accuracy.
    """
    img      = cv2.imread(image_path)
    gray     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, thresh = cv2.threshold(
        denoised, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresh


def extract_lines_from_image(image_path):
    """
    Splits the page image into individual lines.
    TrOCR works best on one line at a time.
    """
    img         = cv2.imread(image_path)
    gray        = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary   = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Find horizontal line regions
    kernel      = cv2.getStructuringElement(
        cv2.MORPH_RECT, (40, 1)
    )
    dilated     = cv2.dilate(binary, kernel, iterations=2)
    contours, _ = cv2.findContours(
        dilated,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Sort contours top to bottom
    contours = sorted(
        contours, key=lambda c: cv2.boundingRect(c)[1]
    )

    line_images = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter out very small regions (noise)
        if h > 10 and w > 50:
            # Add padding around each line
            pad    = 5
            y1     = max(0, y - pad)
            y2     = min(img.shape[0], y + h + pad)
            x1     = max(0, x - pad)
            x2     = min(img.shape[1], x + w + pad)
            line   = img[y1:y2, x1:x2]
            line_images.append(line)

    return line_images


def read_line_with_trocr(line_image):
    """
    Uses TrOCR to read text from a single line image.
    """
    # Convert BGR to RGB
    rgb    = cv2.cvtColor(line_image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    # Process image for model
    pixel_values = processor(
        images=pil_img, return_tensors="pt"
    ).pixel_values

    # Generate text
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)

    # Decode output
    text = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    return text.strip()


def extract_text_from_image(image_path):
    """
    Full pipeline — splits page into lines,
    reads each line with TrOCR, joins results.
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")

    # Extract individual lines from the page
    line_images = extract_lines_from_image(image_path)
    print(f"  Lines detected: {len(line_images)}")

    if not line_images:
        print("  ⚠️ No lines detected — trying full page mode")
        img     = cv2.imread(image_path)
        rgb     = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pixel_values = processor(
            images=pil_img, return_tensors="pt"
        ).pixel_values
        with torch.no_grad():
            generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        return text

    # Read each line
    lines = []
    for i, line_img in enumerate(line_images):
        text = read_line_with_trocr(line_img)
        if text.strip():
            lines.append(text)
            print(f"  Line {i+1}: {text}")

    full_text = '\n'.join(lines)
    print(f"\n  Total lines read : {len(lines)}")
    print(f"  Total words      : {len(full_text.split())}")
    return full_text


def extract_text_from_all_images(output_folder):
    """
    Finds all page images and extracts text from each.
    """
    image_files = sorted([
        f for f in os.listdir(output_folder)
        if f.startswith('page_') and f.endswith('.png')
    ])

    if not image_files:
        print("⚠️ No page images found. Run convert.py first!")
        return {}

    print(f"Found {len(image_files)} page image(s) to process")
    all_text = {}

    for image_file in image_files:
        image_path = os.path.join(output_folder, image_file)
        page_num   = image_file.replace(
            'page_', '').replace('.png', '')
        text = extract_text_from_image(image_path)
        all_text[f"page_{page_num}"] = text

    return all_text


def save_extracted_text(all_text, output_folder):
    """
    Saves extracted text to .txt and .json files.
    """
    txt_path = os.path.join(output_folder, "extracted_text.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        for page, text in all_text.items():
            f.write(f"{'='*50}\n")
            f.write(f"PAGE {page.replace('page_','').upper()}\n")
            f.write(f"{'='*50}\n")
            f.write(text)
            f.write("\n\n")

    json_path = os.path.join(
        output_folder, "extracted_text.json"
    )
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_text, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Text saved: extracted_text.txt")
    print(f"✅ Text saved: extracted_text.json")
    return txt_path


# ── Run it ───────────────────────────────────────────────────
if __name__ == "__main__":
    all_text = extract_text_from_all_images(OUTPUT_DIR)

    if all_text:
        save_extracted_text(all_text, OUTPUT_DIR)

        print("\n========== OCR SUMMARY ==========")
        total_words = sum(
            len(t.split()) for t in all_text.values()
        )
        total_chars = sum(
            len(t) for t in all_text.values()
        )
        print(f"Pages processed  : {len(all_text)}")
        print(f"Total words      : {total_words}")
        print(f"Total characters : {total_chars}")
        print("==================================")

        print("\n=== TEXT PREVIEW ===")
        first_text = list(all_text.values())[0]
        print(first_text)