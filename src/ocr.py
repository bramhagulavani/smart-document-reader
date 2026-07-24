import os
import sys
import json
import easyocr
import cv2
import numpy as np

# Configure standard output to UTF-8 for Windows PowerShell compatibility
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── Path Setup ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")

# ── Load EasyOCR Model ───────────────────────────────────────
print("Loading EasyOCR model...")
print("(First time only — downloads AI model, please wait...)")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ EasyOCR model loaded!")


def preprocess_image(image_path):
    """
    Advanced preprocessing specifically for
    phone-captured handwriting on white paper.
    """
    img = cv2.imread(image_path)

    # ── Step 1: Resize for better OCR ────────────────────────
    # EasyOCR works best on images around 1800-2400px wide
    h, w  = img.shape[:2]
    if w > 2400:
        scale = 2400 / w
        img   = cv2.resize(
            img, (2400, int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

    # ── Step 2: Convert to grayscale ─────────────────────────
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ── Step 3: Fix uneven lighting / shadows ────────────────
    # This removes the shadow effect from phone camera
    blur        = cv2.GaussianBlur(gray, (0, 0), 51)
    shadow_free = cv2.divide(gray, blur, scale=255)

    # ── Step 4: Boost contrast ────────────────────────────────
    clahe    = cv2.createCLAHE(
        clipLimit=3.0, tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(shadow_free)

    # ── Step 5: Sharpen the image ────────────────────────────
    kernel    = np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
    ])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    # ── Step 6: Denoise ──────────────────────────────────────
    denoised = cv2.fastNlMeansDenoising(sharpened, h=10)

    # ── Step 7: Final threshold ───────────────────────────────
    _, thresh = cv2.threshold(
        denoised, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Save preprocessed image
    temp_path = image_path.replace('.png', '_processed.png')
    cv2.imwrite(temp_path, thresh)

    return temp_path
    
def extract_text_from_image(image_path):
    """
    Uses EasyOCR to extract text from a single page image.
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")

    # Preprocess the image
    processed_path = preprocess_image(image_path)

    # Run EasyOCR — returns list of [bbox, text, confidence]
    results = reader.readtext(
    processed_path,
    paragraph=True,
    width_ths=0.9,
    height_ths=0.9,
    contrast_ths=0.05,
    text_threshold=0.4,
    low_text=0.3,
    link_threshold=0.4
    )

    # Sort results top to bottom by y coordinate
    results = sorted(results, key=lambda x: x[0][0][1])

    # Extract text lines with confidence
    lines      = []
    total_conf = 0

    for (bbox, text, confidence) in results:
        if confidence > 0.1:  # filter very low confidence
            lines.append(text)
            total_conf += confidence
            print(f"  [{confidence*100:.0f}%] {text}")

    avg_conf  = (total_conf / len(results)) * 100 if results else 0
    full_text = '\n'.join(lines)

    print(f"\n  Lines detected   : {len(lines)}")
    print(f"  Words extracted  : {len(full_text.split())}")
    print(f"  Avg confidence   : {avg_conf:.1f}%")

    # Clean up temp file
    if os.path.exists(processed_path):
        os.remove(processed_path)

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
    # First convert your handwritten PDF
    # Make sure convert.py was run first!
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

        print("\n=== EXTRACTED TEXT ===")
        for page, text in all_text.items():
            print(f"\n{page.upper()}:")
            print(text)