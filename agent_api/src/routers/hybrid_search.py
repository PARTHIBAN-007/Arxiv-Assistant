from loguru import logger
from fastapi import APIRouter, HTTPException
from src.dependencies import EmbeddingsDep,OpenSearchDep

from pydantic import BaseModel,Field
from typing import List,Optional

class HybridSearchRequest(BaseModel):
    """Request model for hybrid search supporting all search modes."""

    query: str = Field(..., description="Search query text", min_length=1, max_length=500)
    size: int = Field(10, description="Number of results to return", ge=1, le=100)
    from_: int = Field(0, description="Offset for pagination", ge=0, alias="from")
    categories: Optional[List[str]] = Field(None, description="Filter by arXiv categories (e.g., ['cs.AI', 'cs.LG'])")
    latest_papers: bool = Field(False, description="Sort by publication date instead of relevance")
    use_hybrid: bool = Field(True, description="Enable hybrid search (BM25 + vector) with automatic embedding generation")
    min_score: float = Field(0.0, description="Minimum score threshold for results", ge=0.0)

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "query": "machine learning neural networks",
                "size": 10,
                "categories": ["cs.AI", "cs.LG"],
                "latest_papers": False,
                "use_hybrid": True,
            }
        }


class SearchHit(BaseModel):
    """Individual search result."""

    arxiv_id: str
    title: str
    authors: Optional[str]
    abstract: Optional[str]
    published_date: Optional[str]
    pdf_url: Optional[str]
    score: float
    highlights: Optional[dict] = None

    # Chunk-specific fields (for unified search)
    chunk_text: Optional[str] = Field(None, description="Text content of the matching chunk")
    chunk_id: Optional[str] = Field(None, description="Unique identifier of the chunk")
    section_name: Optional[str] = Field(None, description="Section name where the chunk was found")


class SearchResponse(BaseModel):
    """Search response model."""

    query: str
    total: int
    hits: List[SearchHit]
    size: int = Field(description="Number of results requested")
    from_: int = Field(alias="from", description="Offset used for pagination")
    search_mode: Optional[str] = Field(None, description="Search mode used: bm25, vector, or hybrid")
    error: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

router = APIRouter(prefix="/hybrid-search",tags =["hybrid-search"])

@router.post("/",response_model = SearchResponse)
async def hybrid_search(
    request:HybridSearchRequest,opensearch_client:OpenSearchDep,embeddings_service: EmbeddingsDep
)->SearchResponse:
    try:
        if not opensearch_client.health_check():
            raise HTTPException(status_code=503,detail = "Search Service is currently unavailable")
        
        query_embedding = None
        if request.use_hybrid:
            try:
                query_embedding = await embeddings_service.embed_query(request.query)
                logger.info("Generated Query Embedding for hybrid search")
            except Exception as e:
                logger.warning(f"Failed to generate embedding for the query")
                query_embedding = None
        logger.info(f"Hybrud Seach: {request.query} (hybrid: {request.use_hybrid and query_embedding is not None})")

        results = opensearch_client.search_unified(
            query = request.query,
            query_embedding = query_embedding,
            size = request.size,
            from_ = request.categories,
            latest = request.latest_papers,
            use_hybrid = request.use_hybrid,
            min_score = request.min_score,
        )

        hits = []
        for hit in results.get("hits",[]):
            hits.append(
                SearchHit(
                    arxiv_id = hit.get("arxiv_id",""),
                    title = hit.get("title",""),
                    authors = hit.get("authors",""),
                    published_date = hit.get("published_data",""),
                    pdf_url=hit.get("pdf_url"),
                    score=hit.get("score", 0.0),
                    highlights=hit.get("highlights"),
                    chunk_text=hit.get("chunk_text"),
                    chunk_id=hit.get("chunk_id"),
                    section_name=hit.get("section_name"),

                )
            )
        search_response = SearchResponse(
            query = request.query,
            total = results.get("total",0),
            hits = hits,
            size = request.size,
             **{"from": request.from_},
            search_mode="hybrid" if (request.use_hybrid and query_embedding) else "bm25",
        )

        return search_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hybrid Search Error: {e}")
        raise HTTPException(status_code=500,detail = f"Search failed: {str(e)}")