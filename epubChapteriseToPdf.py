import os
import zipfile
import re
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_epub(epub_path, extract_path):
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def find_chapter_files(extract_path):
    chapter_files = []
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.endswith(('.html', '.xhtml', '.htm')):
                chapter_files.append(os.path.join(root, file))
    chapter_files.sort()  # Sort files to maintain order
    return chapter_files

def extract_text_from_html(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        # Extract text while preserving some basic formatting
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for p in soup.find_all("p"):
            p.insert(0, "\n\n")
        return soup.get_text()

def create_pdf_from_text(text, pdf_file):
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for paragraph in text.split('\n\n'):
        if paragraph.strip():
            p = Paragraph(paragraph.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))  # Add space between paragraphs

    doc.build(story)

def main(epub_file):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    extract_path = os.path.join(base_dir, 'extracted_epub')
    pdf_output_path = os.path.join(base_dir, 'BGE')
    
    # Create output directory if it doesn't exist
    os.makedirs(pdf_output_path, exist_ok=True)
    
    extract_epub(epub_file, extract_path)
    chapter_files = find_chapter_files(extract_path)

    for i, chapter_file in enumerate(chapter_files, 1):
        pdf_file = os.path.join(pdf_output_path, f'chapter_{i}.pdf')
        try:
            text = extract_text_from_html(chapter_file)
            create_pdf_from_text(text, pdf_file)
            logger.info(f'Successfully converted {chapter_file} to {pdf_file}')
        except Exception as e:
            logger.error(f"Failed to convert {chapter_file}: {str(e)}")

    logger.info('Conversion complete!')

if __name__ == '__main__':
    epub_file = os.path.abspath("/Users/vaibhavsrivastava/Documents/Dev/EpubChapteriseToPDF/pg4363-images-3.epub")  # Replace with your EPUB file path
    main(epub_file)