import os
import re
from fpdf import FPDF

# ── Path Setup ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")

def clean_text(text):
    """
    Cleans raw OCR text — removes noise, fixes spacing.
    """
    # Remove non-printable characters
    # Remove non-printable and special unicode characters
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
    # Replace common special characters with ASCII equivalents
    text = text.replace('\u2014', '-')   # em dash
    text = text.replace('\u2013', '-')   # en dash
    text = text.replace('\u2018', "'")   # left single quote
    text = text.replace('\u2019', "'")   # right single quote
    text = text.replace('\u201c', '"')   # left double quote
    text = text.replace('\u201d', '"')   # right double quote
    text = text.replace('\u2022', '-')   # bullet point

    # Fix multiple spaces
    text = re.sub(r' +', ' ', text)

    # Fix multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]

    # Remove completely empty lines at start and end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return '\n'.join(lines)


class CleanPDF(FPDF):
    """
    Custom PDF class with header and footer.
    """
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Smart Document Reader - Extracted Text',
                  align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Page {self.page_no()}',
                  align='C')


def generate_clean_pdf(extracted_text_path, output_pdf_path):
    """
    Reads extracted text file and generates a clean PDF.
    """
    # Read the extracted text
    with open(extracted_text_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    print(f"Raw text loaded: {len(raw_text)} characters")

    # Clean the text
    cleaned_text = clean_text(raw_text)
    print(f"Cleaned text  : {len(cleaned_text)} characters")

    # Create PDF
    # Create PDF
    pdf = CleanPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Set font
    pdf.set_font('Helvetica', size=11)
    pdf.set_text_color(30, 30, 30)

    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Write each line
    lines = cleaned_text.split('\n')
    for line in lines:
        if line.strip() == '':
            pdf.ln(4)  # blank line spacing
        else:
            # Check if line looks like a heading
            # (short line, all caps or ends with colon)
            is_heading = (
                len(line) < 60 and
                (line.isupper() or line.endswith(':'))
            )

            if is_heading:
                pdf.set_font('Helvetica', 'B', 12)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_font('Helvetica', size=11)
                pdf.set_text_color(30, 30, 30)

            # Write the line
            pdf.multi_cell(content_width, 7, line, new_x='LMARGIN', new_y='NEXT')

    # Save the PDF
    pdf.output(output_pdf_path)
    print(f"\n✅ Clean PDF saved: {output_pdf_path}")
    return output_pdf_path


# ── Run it ───────────────────────────────────────────────────
if __name__ == "__main__":
    extracted_text_path = os.path.join(OUTPUT_DIR,
                                        "extracted_text.txt")
    output_pdf_path     = os.path.join(OUTPUT_DIR,
                                        "clean_output.pdf")

    if not os.path.exists(extracted_text_path):
        print("⚠️ extracted_text.txt not found!")
        print("   Please run ocr.py first.")
    else:
        generate_clean_pdf(extracted_text_path, output_pdf_path)

        print("\n========== GENERATOR SUMMARY ==========")
        print(f"Input  : extracted_text.txt")
        print(f"Output : clean_output.pdf")
        size = os.path.getsize(output_pdf_path) / 1024
        print(f"PDF size : {size:.1f} KB")
        print("=======================================")