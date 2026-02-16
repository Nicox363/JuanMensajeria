from PyPDF2 import PdfReader, PdfWriter, PageObject
import io

def add_blank_page_to_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Add blank page
    # Get size of last page to match
    if len(reader.pages) > 0:
        last_page = reader.pages[-1]
        width = last_page.mediabox.width
        height = last_page.mediabox.height
        writer.add_blank_page(width=width, height=height)
    else:
        writer.add_blank_page(width=612, height=792) # Default Letter

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

if __name__ == "__main__":
    # Create a dummy pdf first for testing
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("test_original.pdf")
    c.drawString(100, 750, "Hello World")
    c.save()
    
    add_blank_page_to_pdf("test_original.pdf", "test_with_blank.pdf")
    print("PDF created: test_with_blank.pdf")
