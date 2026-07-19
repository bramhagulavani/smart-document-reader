# 📄 Smart Document Reader

> An AI-powered OCR tool that reads scanned, damaged or unclear PDF documents
> and extracts clean, readable text — served through an interactive Streamlit web app.

**Built by Bramha Gulavani | VIT Pune | AI & ML Engineering | 2nd Year**

---

## 🖥️ Demo

![App Screenshot](outputs/app_screenshot.png)

> Upload any scanned PDF → AI extracts the text → Download clean readable output instantly

---

## 📌 Project Roadmap

### ✅ Version A — English OCR (Current)

| Step | Description | Status |
|------|-------------|--------|
| Step 1 | PDF to Image conversion using PyMuPDF | ✅ Done |
| Step 2 | OCR text extraction using Tesseract | ✅ Done |
| Step 3 | Text cleaning + Clean PDF generation | ✅ Done |
| Step 4 | Streamlit dashboard — upload + download | ✅ Done |

### 🔜 Version B — Marathi + Advanced (Coming Soon)

| Step | Description | Status |
|------|-------------|--------|
| Step 5 | Marathi language support | 🔜 Planned |
| Step 6 | Handwriting recognition | 🔜 Planned |
| Step 7 | Side by side comparison view | 🔜 Planned |
| Step 8 | Final deployment | 🔜 Planned |

---

## 🛠️ Tech Stack

- **Language** — Python
- **PDF Processing** — PyMuPDF (fitz)
- **Image Processing** — OpenCV, Pillow
- **OCR Engine** — Tesseract v5.5.0, pytesseract
- **PDF Generation** — fpdf2
- **Web App** — Streamlit
- **Data** — pandas, numpy

---

## 📂 Folder Structure

```
smart-document-reader/
├── data/
│   ├── sample_inputs/        ← place your PDF files here
│   └── outputs/              ← extracted images + text saved here
├── src/
│   ├── convert.py            ← Step 1: PDF to image conversion
│   ├── ocr.py                ← Step 2: OCR text extraction
│   ├── generator.py          ← Step 3: Clean PDF generation
│   └── app.py                ← Step 4: Streamlit web app
├── outputs/                  ← final output files
├── venv/                     ← virtual environment
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/BramhaGulavani/smart-document-reader.git
cd smart-document-reader
```

**2. Install Tesseract OCR Engine**

Download and install from:
👉 https://github.com/UB-Mannheim/tesseract/wiki

- Download `tesseract-ocr-w64-setup-5.x.x.exe`
- Keep default path: `C:\Program Files\Tesseract-OCR\`
- ✅ Check **Add to PATH** during installation

Verify installation:
```bash
tesseract --version
```

**3. Create and activate virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If PowerShell blocks the script, run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**4. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**5. Run the Streamlit app**
```bash
streamlit run src/app.py
```

---

## 🧠 How It Works

```
User uploads a scanned PDF
          ↓
Each page converted to high quality image (300 DPI)
          ↓
Image preprocessed — grayscale + denoise + threshold
          ↓
Tesseract OCR reads text from cleaned image
          ↓
Text cleaned and formatted
          ↓
Clean readable PDF generated
          ↓
User downloads the clean PDF
```

---

## ⚙️ How Each File Works

| File | What it does |
|------|-------------|
| `convert.py` | Opens PDF using PyMuPDF, converts each page to a 300 DPI PNG image |
| `ocr.py` | Preprocesses image using OpenCV, runs Tesseract OCR, saves extracted text |
| `generator.py` | Takes extracted text, cleans it, generates a new formatted PDF using fpdf2 |
| `app.py` | Streamlit dashboard — upload PDF, run full pipeline, preview and download result |

---

## 💡 Key Concepts Learned

- **OCR (Optical Character Recognition)** — teaching a machine to read text from images
- **Image Preprocessing** — grayscale conversion, denoising, thresholding to improve OCR accuracy
- **PDF Processing** — reading and generating PDF files programmatically
- **Pipeline Architecture** — chaining multiple steps where output of one becomes input of next
- **Streamlit File Uploader** — handling file uploads and downloads in a web app

---

## 📋 Requirements

```
pymupdf
Pillow
pytesseract
fpdf2
streamlit
pandas
numpy
opencv-python
```

Install all:
```bash
pip install -r requirements.txt
```

> Also requires Tesseract OCR installed separately on Windows

---

## ⚠️ Notes

- For best OCR results use clear, high resolution scanned PDFs
- Handwritten text accuracy depends on handwriting clarity
- Marathi language support coming in Version B
- This project is for educational and portfolio purposes

---

## 📄 License

Free to use for learning and portfolio purposes.

---

## 🙋 About Me

**Bramha Gulavani**
2nd Year AI & ML Engineering Student at VIT Pune
Building real-world AI projects from scratch — one step at a time.

[![GitHub](https://img.shields.io/badge/GitHub-BramhaGulavani-black?style=flat&logo=github)](https://github.com/BramhaGulavani)

---

## 🗂️ My Other Projects

| Project | Description | Tech |
|---------|-------------|------|
| [🧠 Fake News Detector](https://github.com/BramhaGulavani/fake-news-detector) | Detects fake news using NLP + Logistic Regression | NLP, TF-IDF, Streamlit |
| [🎓 Student Score Predictor](https://github.com/BramhaGulavani/student-score-predictor) | Predicts student math scores using 3 Regression models | Linear Regression, XGBoost, Streamlit |
| [📄 Smart Document Reader](https://github.com/BramhaGulavani/smart-document-reader) | Reads scanned PDFs and generates clean output using OCR | OCR, OpenCV, Tesseract, Streamlit |