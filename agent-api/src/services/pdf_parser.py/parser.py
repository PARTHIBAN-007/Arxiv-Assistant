from loguru import logger
from pathlib import Path
from typing import Optional

from src.exceptions import PDFParsingException , PDFValidationError
from src.schemas.pdf_parser.models import PdfContent

from .docling import DoclingParser

class PDFParserService:
    """PDF Parsing using DOcling"""

    def __init__(self,max_pages:int,max_file_size_mb:int,do_ocr:bool= False,do_table_structure:bool= True):
        """Initialize PDF Parser service with configurable limits"""

        self.docling_parser = DoclingParser(
            max_pages = max_pages,
            max_file_size_mb = max_file_size_mb,
            do_ocr = do_ocr,
            do_table_structure = do_table_structure
        )

    async def parse_pdf(self,pdf_path:Path)->Optional[PdfContent]:
        """Parse pDF using Docling"""
        if not pdf_path.exists():
            logger.error(f"PDF File not Found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")
        try:
            result = await self.docling_parser.parse_pdf(pdf_path)
            if result:
                logger.info(f"Parsed  {pdf_path}")
                return result
            else:
                logger.error(f"Docling Parsing returned no results fro {pdf_path.name}")
                raise PDFParsingException(f"Docling Parsing returned no results for {pdf_path.name}")
        except (PDFValidationError,PDFParsingException):
            raise

        except Exception as e:
            logger.error(f"Docling Parsing Error fro {pdf_path.name}: {e}")
            raise PDFParsingException(f"Docling Parsing Error {pdf_path.name}: {e}")