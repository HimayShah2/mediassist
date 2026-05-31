import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF (fitz) not available. Text extraction from PDF might be limited.")

try:
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract or PIL not available. OCR for PDF disabled.")

class PDFParser:
    def __init__(self):
        self.is_available = PYMUPDF_AVAILABLE or TESSERACT_AVAILABLE

    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        if not self.is_available:
            logger.error("PDF parser is not available (PyMuPDF and Tesseract missing).")
            return []
            
        text_content = ""
        
        try:
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(filepath)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text() + "\n"
                    
                    if TESSERACT_AVAILABLE:
                        for img_index, img in enumerate(page.get_images(full=True)):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            try:
                                image = Image.open(io.BytesIO(image_bytes))
                                text_content += pytesseract.image_to_string(image) + "\n"
                            except Exception as ocr_e:
                                logger.warning(f"OCR failed on image in {filepath}: {ocr_e}")
            else:
                logger.error("PyMuPDF is required for PDF parsing currently.")
                
        except Exception as e:
            logger.error(f"Failed to parse PDF {filepath}: {e}")
            
        return [{"text": text_content.strip()}]
