import streamlit as st
import os
import sys
import tempfile
import shutil

# ── Add src to path so we can import our own files ───────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from convert   import convert_pdf_to_images
from ocr       import extract_text_from_all_images, save_extracted_text
from generator import generate_clean_pdf

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title = "Smart Document Reader",
    page_icon  = "📄",
    layout     = "centered"
)

# ── Header ───────────────────────────────────────────────────
st.title("📄 Smart Document Reader")
st.markdown("#### Built by Bramha Gulavani | VIT Pune | AI & ML")
st.markdown("---")

# ── Info Cards ───────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("OCR Engine",   "EasyOCR Deep Learning")
col2.metric("Supported",    "English PDFs")
col3.metric("Output",       "Clean PDF")

st.markdown("---")

# ── Upload Section ───────────────────────────────────────────
st.subheader("📂 Upload your scanned PDF")
st.caption("Upload any scanned or handwritten PDF — "
           "AI will extract and clean the content")

uploaded_file = st.file_uploader(
    label       = "Choose a PDF file",
    type        = ["pdf"],
    label_visibility = "collapsed"
)

# ── Process Button ───────────────────────────────────────────
if uploaded_file is not None:
    st.success(f"✅ File uploaded: **{uploaded_file.name}**")
    st.markdown(f"File size: "
                f"{uploaded_file.size / 1024:.1f} KB")

    st.markdown("---")

    if st.button("🔍 Extract & Generate Clean PDF",
                 use_container_width=True):

        # Create temp working directory
        temp_dir = tempfile.mkdtemp()
        img_dir  = os.path.join(temp_dir, "images")
        os.makedirs(img_dir)

        try:
            # ── Step 1: Save uploaded PDF ─────────────────
            pdf_path = os.path.join(temp_dir,
                                    uploaded_file.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ── Step 2: Convert PDF to images ────────────
            with st.spinner("📸 Converting PDF pages "
                            "to images..."):
                image_paths = convert_pdf_to_images(
                    pdf_path, img_dir, dpi=300
                )
            st.success(f"✅ {len(image_paths)} page(s) converted")

            # ── Step 3: OCR extraction ────────────────────
            with st.spinner("🔍 Extracting text using "
                            "EasyOCR AI model..."):
                all_text = extract_text_from_all_images(img_dir)
                txt_path = save_extracted_text(all_text, temp_dir)
            total_words = sum(
                len(t.split()) for t in all_text.values()
            )
            st.success(f"✅ {total_words} words extracted "
                       f"from {len(all_text)} page(s)")

            # ── Step 4: Generate clean PDF ────────────────
            with st.spinner("📝 Generating clean PDF..."):
                output_pdf = os.path.join(temp_dir,
                                          "clean_output.pdf")
                generate_clean_pdf(txt_path, output_pdf)
            st.success("✅ Clean PDF generated!")

            st.markdown("---")

            # ── Results Section ───────────────────────────
            st.subheader("📊 Extraction Results")

            m1, m2, m3 = st.columns(3)
            m1.metric("Pages",      len(image_paths))
            m2.metric("Words",      total_words)
            m3.metric("Characters", sum(
                len(t) for t in all_text.values()
            ))

            # ── Text Preview ──────────────────────────────
            st.markdown("---")
            st.subheader("👀 Extracted Text Preview")
            first_text = list(all_text.values())[0] if all_text else "No text extracted."
            st.text_area(
                label       = "Extracted Text",
                value       = first_text[:1000] + "...",
                height      = 250,
                disabled    = True,
                label_visibility = "collapsed"
            )

            # ── Download Button ───────────────────────────
            st.markdown("---")
            st.subheader("⬇️ Download Clean PDF")
            with open(output_pdf, "rb") as f:
                st.download_button(
                    label    = "⬇️ Download Clean PDF",
                    data     = f,
                    file_name= "clean_output.pdf",
                    mime     = "application/pdf",
                    use_container_width = True
                )

            st.balloons()

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
            st.caption("Ensure virtual environment with PyTorch and EasyOCR is active.")

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About this Project")
    st.markdown("""
    This app uses **EasyOCR (Deep Learning)** to read text
    from scanned or handwritten PDF documents and
    generates a clean, readable PDF output.

    **How it works:**
    1. Upload your scanned PDF
    2. Each page converts to image
    3. EasyOCR model reads the text
    4. Text gets cleaned & unicode formatted
    5. Clean PDF is generated
    6. Download your clean PDF

    **Best results with:**
    - Clear scanned documents
    - Plain white paper handwriting
    - Good lighting / high contrast
    - English language text
    """)

    st.markdown("---")
    st.markdown("**Tech Stack**")
    st.markdown("- PyMuPDF (fitz)")
    st.markdown("- OpenCV")
    st.markdown("- EasyOCR")
    st.markdown("- PyTorch")
    st.markdown("- fpdf2")
    st.markdown("- Streamlit")

    st.markdown("---")
    st.caption("Built by Bramha Gulavani")
    st.caption("VIT Pune | AI & ML | 2nd Year")