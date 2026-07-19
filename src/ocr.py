import pytesseract
import os
import json
from PIL import Image
import cv2
import numpy as np

# ── Tesseract Path Setup ─────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ── Path Setup ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")

def preprocess_image(image_path):
    """
    Cleans the image before OCR for better accuracy.
    Returns a processed image ready for OCR.
    """
    # Read image using OpenCV
    img = cv2.imread(image_path)

    # Convert to grayscale (black and white)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remove noise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Increase contrast using threshold
    _, thresh = cv2.threshold(
        denoised, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh


def extract_text_from_image(image_path):
    """
    Runs OCR on a single image and returns extracted text.
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")

    # Preprocess the image
    processed = preprocess_image(image_path)

    # Convert processed image back to PIL format for tesseract
    pil_image = Image.fromarray(processed)

    # Run OCR
    config = '--oem 3 --psm 6'
    text   = pytesseract.image_to_string(pil_image, config=config)

    print(f"  Characters extracted: {len(text)}")
    print(f"  Words extracted     : {len(text.split())}")

    return text


def extract_text_from_all_images(output_folder):
    """
    Finds all page images and extracts text from each one.
    Returns a dictionary with page number and extracted text.
    """
    # Find all page images in order
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
        page_num   = image_file.replace('page_', '').replace('.png', '')

        text = extract_text_from_image(image_path)
        all_text[f"page_{page_num}"] = text

    return all_text


def save_extracted_text(all_text, output_folder):
    """
    Saves extracted text to a .txt file and a .json file.
    """
    # Save as plain text
    txt_path = os.path.join(output_folder, "extracted_text.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        for page, text in all_text.items():
            f.write(f"{'='*50}\n")
            f.write(f"PAGE {page.replace('page_', '').upper()}\n")
            f.write(f"{'='*50}\n")
            f.write(text)
            f.write("\n\n")

    # Save as JSON
    json_path = os.path.join(output_folder, "extracted_text.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_text, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Text saved to: extracted_text.txt")
    print(f"✅ Text saved to: extracted_text.json")
    return txt_path


# ── Run it ───────────────────────────────────────────────────
if __name__ == "__main__":
    all_text = extract_text_from_all_images(OUTPUT_DIR)

    if all_text:
        save_extracted_text(all_text, OUTPUT_DIR)

        # Print preview
        print("\n========== OCR SUMMARY ==========")
        total_chars = sum(len(t) for t in all_text.values())
        total_words = sum(len(t.split()) for t in all_text.values())
        print(f"Pages processed  : {len(all_text)}")
        print(f"Total characters : {total_chars}")
        print(f"Total words      : {total_words}")
        print(f"Output folder    : {OUTPUT_DIR}")
        print("==================================")

        print("\n=== TEXT PREVIEW (first 500 chars) ===")
        first_page_text = list(all_text.values())[0]
        print(first_page_text[:500])
        print("...")