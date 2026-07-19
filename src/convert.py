import fitz  # this is pymupdf
import os
from PIL import Image

# ── Path Setup ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR  = os.path.join(BASE_DIR, "data", "sample_inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")

def convert_pdf_to_images(pdf_path, output_folder, dpi=300):
    """
    Converts each page of a PDF into a high quality image.
    Returns a list of image file paths.
    """
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    image_paths = []

    print(f"PDF loaded: {os.path.basename(pdf_path)}")
    print(f"Total pages: {len(pdf_document)}")

    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document[page_num]

        # Convert page to image
        # Matrix controls the resolution — higher = clearer image
        mat  = fitz.Matrix(dpi / 72, dpi / 72)
        pix  = page.get_pixmap(matrix=mat)

        # Save image
        image_filename = f"page_{page_num + 1}.png"
        image_path     = os.path.join(output_folder, image_filename)
        pix.save(image_path)

        image_paths.append(image_path)
        print(f"  ✅ Page {page_num + 1} saved as {image_filename}")

    pdf_document.close()
    print(f"\nAll {len(image_paths)} pages converted to images!")
    return image_paths


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Look for any PDF in sample_inputs folder
    pdf_files = [f for f in os.listdir(INPUT_DIR)
                 if f.endswith('.pdf')]

    if not pdf_files:
        print("⚠️  No PDF found in data/sample_inputs/")
        print("    Please add a PDF file there and run again.")
    else:
        pdf_path = os.path.join(INPUT_DIR, pdf_files[0])
        print(f"Found PDF: {pdf_files[0]}")
        images   = convert_pdf_to_images(pdf_path, OUTPUT_DIR)
        print(f"\n========== CONVERT SUMMARY ==========")
        print(f"PDF file     : {pdf_files[0]}")
        print(f"Pages found  : {len(images)}")
        print(f"Images saved : {OUTPUT_DIR}")
        print(f"=====================================")