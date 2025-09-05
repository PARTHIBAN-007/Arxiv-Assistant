from enum import Enum
from typing import Any, List,Dict, Optional
from pydantic import BaseModel , Field


class ParserType(str,Enum):
    """PDF parser types"""
    DOCLING = "docling"

class PaperSection(BaseModel):
    """Represents a section of a paper"""
    title: str = Field(...,description="section Title")
    content: str = Field(...,description="Section Description")
    level: int = Field(...,description="Section Hierarchy Level")

class PaperFigure(BaseModel):
    """Represents a figure in a paper"""

    caption: str = Field(...,description="Figure Caption")
    id: str = Field(...,description="Figure Identifier")

class PaperTable(BaseModel):
    """Represents a Table in a paper"""
    caption: str = Field(...,description="Table Caption")
    id: str = Field(...,description="Table Identifier")

class PdfContent(BaseModel):
    """PDF Specific content extracted by papers like docling"""

    sections: List[PaperSection] = Field(default_factory=list,description="Paper Section")
    figures: List[PaperFigure] = Field(default_factory=list,description="Figures")
    tables: List[PaperTable] = Field(default_factory=list,description="Tables")
    raw_text: str = Field(...,description="Full Extracted Text")
    references: List[str] = Field(default_factory=list,description="References")
    parser_used: ParserType = Field(...,description="Parser used for extraction")
    metadata: Dict[str,Any] = Field(default_factory=dict,description="Parser Metadata")


class ArxivMetadata(BaseModel):
    """Paper Metadata from Arxiv API"""
    title: str = Field(...,description="Paper title from Arxiv")
    authors: List[str] = Field(...,description="Authors from Arxiv")
    abstract: str = Field(...,description="Abstract from arxiv")
    arxiv_id: str = Field(...,description="arxiv identifier")
    categories: List[str] = Field(default_factory=list,description="arxiv categories")
    published_data: str = Field(...,description="Publication date")
    pdf_url: str = Field(...,description="PDF Download URL")

class ParsedPaper(BaseModel):
    """Complete Paper Data combining Ariv metadata and Paper Content"""
    arxiv_metadata : ArxivMetadata = Field(...,description="Metadata from Arxiv API")
    pdf_content: Optional[PdfContent] = Field(None,description="Content extracted from PDF")

