from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import io
import os
from django.conf import settings

def generate_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    field_positions = {
        'narration': (50, 700),
        'credit': (50, 650),
        'account_name': (50, 600),
        'financial_date': (50, 550),
        'nuban': (50, 500),
    }
    
    for field, (x, y) in field_positions.items():
        value = str(data.get(field, 'N/A')).split('by', 1)[1].strip() if field == 'narration' and 'by' in str(data.get(field, '')) else str(data.get(field, 'N/A'))
        c.drawString(x, y, value[:100])  # Limit length to avoid overflow
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    new_pdf = PdfReader(buffer)
    output = PdfWriter()
    
    background_path = os.path.join(settings.STATIC_ROOT, 'xel/background.pdf')
    if os.path.exists(background_path):
        background_pdf = PdfReader(open(background_path, 'rb'))
        page = new_pdf.pages[0]
        page.merge_page(background_pdf.pages[0])
        output.add_page(page)
    else:
        output.add_page(new_pdf.pages[0])
    
    output_buffer = io.BytesIO()
    output.write(output_buffer)
    pdf_content = output_buffer.getvalue()
    buffer.close()
    output_buffer.close()
    
    return pdf_content