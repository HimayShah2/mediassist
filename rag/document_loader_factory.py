from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader

try:
    from langchain_community.document_loaders import PDFPlumberLoader
except ImportError:
    PDFPlumberLoader = None

class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path: str, fallback_pdf: bool = False):
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            if fallback_pdf and PDFPlumberLoader:
                return PDFPlumberLoader(str(path))
            return PyMuPDFLoader(str(path))
        elif ext == ".docx":
            return Docx2txtLoader(str(path))
        elif ext == ".txt":
            return TextLoader(str(path))
        else:
            raise ValueError(f"Unsupported file type: {ext}")
