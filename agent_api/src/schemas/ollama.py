from typing import List , Optional

from pydantic import BaseModel , Field

class RAGResponse(BaseModel):
    answer: str = Field(desciption = "Comprehensive answer based on the provided paper")
    sources: List[str] = Field(
        default_factory = list,
        description = "List of PDF URLs from papers"
    )
    confidence: Optional[str] = Field(
        default = None,
        description = "Confidence level , high , medium or low"
    )
    citiations = Optional[list[str]] = Field(
        default = None,
        description = "Specific arxiv IDS or papers titles referred in the answer"
    )