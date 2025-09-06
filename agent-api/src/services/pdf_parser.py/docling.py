from loguru import logger
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfpipelineOptions
from docling.document_converter import DocumentConverter,PdfFormatOption
from src.exceptions import PDFParsingException, PDFValidationError
from src.schemas.pdf_parser.models import PaperFigure , PaperSection,ParserType,PdfContent

class DoclingParser:
    """DOcling PDF parser for scientific document Processing."""

    def _init__(self,max_pages:int,max_file_size_mb:int,do_ocr:bool = False,do_table_Structure:bool = True):
        """Initialize DOcumentCOnverter with Optimized Pipeline options"""
        pipeline_options  = PdfpipelineOptions(
            do_table_Structure = do_table_Structure,
            do_ocr = do_ocr,
        )
        self._converter = DocumentConverter(format_options={InputFormat.PDF : PdfFormatOption(pipeline_options=pipeline_options)})
        self._warmed_up = False
        self.max_pages = max_pages
        self.max_file_size_bytes = max_file_size_mb *1024*1024

    def _warm_up_models(self):
        """Pre Warm the models to avoid cold start"""
        if not self._warmed_up:
            self._warmed_up =True

    def _validate_pdf(self,pdf_path:Path)->bool:
        """Comprehensive PDF Validation including size and page limits"""
        try:
            if pdf_path.stat().st_size ==0:
                logger.error(f"PDF File is Empty: {pdf_path}")
                raise PDFValidationError(f"PDF File is Empty: {pdf_path}")
            file_size = pdf_path.stat().st_size
            if file_size>self.max_file_size_bytes:
                logger.warning(f"PDF File Size {file_size/1024/1024:.1f}MB exceeds limit {self.max_file_size_bytes /1024 / 1024:.1f}MB , Skipping Process")
                raise PDFValidationError(f"PDF File Too Large : {file_size/1024/1024:.1f}MB")
            
            with open(pdf_path,"rb") as f:
                header = f.read(8)
                if not header.startswith(b"%PDF-"):
                    logger.error(f"File Does not have pDF Header: {pdf_path}")
                    raise PDFValidationError(f"File does not havve PDF header: {pdf_path}")
            pdf_doc = pdfium.PdfDocument(str(pdf_path))
            number_of_pages = len(pdf_doc)
            pdf_doc.close()

            if number_of_pages>self.max_pages:
                logger.warning(f"PDF has {number_of_pages} , exceeding limit of {self.max_pages}, skipping processing to avoid performance issues")
                raise PDFValidationError(f"PDF Has too many pages: {number_of_pages}> {self.max_pages}")
            return True
        except PDFValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error Validating PDF {pdf_path}: {e}")


    async def parse_pdf(self,pdf_path:Path)->Optional[PdfContent]:
        """parse PDF using Docling Parser
        Limited to 20 pages to avoid memory issues with large papers"""

        try:
            self._validate_pdf(pdf_path)
            self._warm_up_models()

            result = self._converter.convert(str(pdf_path),max_file_size=self.max_file_size_bytes,max_num_pages=self.max_pages)

            doc = result.document

            sections = []
            current_section = {"title": "Content","content":""}

            for element in doc.texts:
                if hasattr(element,"labels") and element.label in ["title","section_header"]:
                    if current_section["content"].strip():
                        sections.append(PaperSection(title=current_section["title"],content =current_section["content"].strip()))

                    current_section = {"title": element.text.strip(),"content":""}

                else:
                    if hasattr(element,"text") and element.text:
                        current_section["content"] += element.text + "\n"
            if current_section["content"].strip():
                sections.append(PaperSection(title=current_section["title"],content = current_section["content"].strip()))

            return PdfContent(
                sections = sections,
                figures = [],
                labels = [],
                raw_text = doc.export_to_text(),
                references= [],
                parser_used = ParserType.DOCLING,
                metadata={"source":"docling","note":"Content Extracted from PDF, metadata comes from ArXiv API"}
            )

        except Exception as e:
            error_msg = str(e).lower()

            if "too large" in error_msg or "too many pages" in error_msg:
                logger.info(f"Skipping PDF Processing due to size/page Limits: {e}")
                return None
            else:
                raise
        except Exception as e:
            logger.error(f"Failes to parse PDF with Docling : {e}")
            logger.error(f"PDF Path: {pdf_path}")
            logger.error(f"PDF Size: {pdf_path.stat().st_size} bytes")
            logger.error(f"Error Type: {type(e).__name__}")

            error_msg = str(e).lower()

            if "not valid" in error_msg:
                logger.error(f"PDF Appears to be corrupted or not a valid PDF File")
                raise PDFParsingException(f"PDF Appears to be corrupted ot not a valid PDF File")
            elif "timeout" in error_msg:
                logger.error(f"PDF Processing timed out - file may be too complex")
                raise PDFParsingException(f"PDF Processing timed out: {pdf_path}")
            elif "memory" in error_msg or "ram" in error_msg:
                logger.error("Out of memory - PDF may be too large or Complex")
                raise PDFParsingException(f"Out of Memory Processing PDF: {pdf_path}")
            elif "max_num_pages" in error_msg or "page" in error_msg:
                logger.error(f"PDF Processing issue likely related to page limits. limit : {self.max_pages} pages")
                raise PDFParsingException(f"PDF Procesing failes,possibly due to page limit.Limit: {self.max_pages} Pages")
            else:
                raise PDFParsingException(f"Failed to Parse PDF with DOcling: {e}")




