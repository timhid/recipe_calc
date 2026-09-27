import pypdfium2 as pdfium


def extract_text(data: bytes) -> str:
    """Return the text of every page in the PDF, pages joined by newlines."""
    pdf = pdfium.PdfDocument(data)
    try:
        return "\n".join(page.get_textpage().get_text_range() for page in pdf)
    finally:
        pdf.close()
