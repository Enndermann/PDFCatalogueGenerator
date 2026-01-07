import fitz  # PyMuPDF
from PIL import Image
import io

def extract_toc_images(pdf_path, page_numbers, dpi=150):
    """
    Renders specified pages from a PDF to PIL Images.
    page_numbers: list of int (1-based index)
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in page_numbers:
        # Convert 1-based to 0-based
        idx = page_num - 1
        if 0 <= idx < len(doc):
            page = doc.load_page(idx)
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
        else:
            print(f"Warning: Page {page_num} is out of range.")
            
    doc.close()
    return images

def write_toc_to_pdf(pdf_path: str, toc_data: list, offset: int, output_path: str):
    """
    Writes the TOC to the PDF.
    toc_data: list of tuples/dicts with keys 'level', 'title', 'page'
              'page' is the printed page number in the book.
              Actual PDF page index = page - offset.
    offset: int, the difference between PDF page index and printed page number.
            If PDF page 10 is printed page 1, offset is 9.
            Logic: pdf_index = printed_page + offset - 1 (usually) -> Wait, user said "PDF页码与书中页码之差"
            Usually: PDF Page Index (0-based) = Printed Page Number + Offset_Correction.
            
            Let's clarify user definition: "PDF页码与书中页码之差".
            If Printed Page 1 is on PDF Page 15 (1-based), 
            Then PDF Page 15 should lead to Printed Page 1.
            
            Let's assume "Offset" means: PDF_Page_Number (1-based) - Printed_Page_Number
            Example: Printed Page 1 is on PDF Page 15. Offset = 15 - 1 = 14.
            Target PDF Page (0-based) = Printed Page + Offset - 1
            
    """
    doc = fitz.open(pdf_path)
    
    # toc format for PyMuPDF: [lvl, title, page, dest]
    # page is 1-based in older versions, but set_toc expects list of [lvl, title, page] usually.
    # Actually doc.set_toc(toc) expects a list of lists: [lvl, title, page_num, ...] 
    # page_num is 1-based destination page number.
    
    final_toc = []
    for item in toc_data:
        try:
            level = int(item['level'])
            title = item['title']
            printed_page = int(item['page'])
            
            # user input: offset = PDF页码 - 书中页码
            # So: PDF页码 = 书中页码 + offset
            target_pdf_page_1based = printed_page + offset
            
            # Clamp to valid range
            target_pdf_page_1based = max(1, min(target_pdf_page_1based, len(doc)))
            
            final_toc.append([level, title, target_pdf_page_1based])
        except ValueError:
            continue
            
    doc.set_toc(final_toc)
    doc.save(output_path)
    doc.close()
