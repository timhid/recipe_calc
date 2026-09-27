import pypdfium2 as pdfium
text = "\n".join(
    p.get_textpage().get_text_range() 
    for p in pdfium.PdfDocument("sticky.pdf")
)

print(text)