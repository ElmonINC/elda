import os
from PyPDF2 import PdfReader
from docx import Document
import openpyxl
import pandas as pd
import re
from typing import Tuple, Optional

def extract_text(file_path: str) -> Tuple[str, str]:
    """
    Extract text from various file types and generate a preview.
    Returns a tuple of (full_text, preview_text)
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                return text, generate_preview(text)
                
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text, generate_preview(text)
            
        elif ext in ['.docx', '.doc']:
            doc = Document(file_path)
            text = ''
            for para in doc.paragraphs:
                text += para.text + '\n'
            return text, generate_preview(text)
            
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, engine='openpyxl')
            text = df.to_string()
            return text, generate_preview(text)
            
        elif ext in ['.csv']:
            df = pd.read_csv(file_path)
            text = df.to_string()
            return text, generate_preview(text)
            
        else:
            return '', 'Unsupported file type'
            
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return '', f'Error processing file: {str(e)}'

def generate_preview(text: str, max_length: int = 500) -> str:
    """
    Generate a preview of the text with a maximum length.
    """
    if not text:
        return ''
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_length:
        return text
        
    # Find the last complete word within max_length
    preview = text[:max_length]
    last_space = preview.rfind(' ')
    if last_space > 0:
        preview = preview[:last_space]
    
    return preview + '...'

def find_matches(text: str, query: str, context_chars: int = 100) -> list:
    """
    Find matches of the query in the text and return them with context.
    Returns a list of tuples (match_text, start_pos, end_pos)
    """
    matches = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    
    for match in pattern.finditer(text):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        
        # Get the context
        context = text[start:end]
        
        # Add ellipsis if we're not at the start/end of the text
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'
            
        matches.append((context, match.start(), match.end()))
    
    return matches