import os
from PyPDF2 import PdfReader
from docx import Document
import openpyxl

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.txt':
            with open(file_path, 'r') as f:
                return f.read()
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text
        elif ext == '.docx':
            doc = Document(file_path)
            text = ''
            for para in doc.paragraphs:
                text += para.text + '\n'
            return text
        elif ext == '.xlsx':
            wb = openpyxl.load_workbook(file_path)
            text = ''
            for sheet in wb:
                for row in sheet.iter_rows():
                    for cell in row:
                        text += str(cell.value) + ' '
                text += '\n'
            return text
        else:
            return ''  # For .exe and unsupported types
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ''