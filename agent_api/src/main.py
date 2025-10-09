import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from loguru import logger

from src.config import get_settings
from src.db.factory import make_database
from src.routers import hybrid_search, ping
from src.routers.ask import ask_router, stream_router
from src.services.arxiv.factory import make_arxiv_client
from src.services.cache.factory import make_cache_client
from src.services.embeddings.factory import make_embeddings_service
from src.services.langfuse.factory import make_langfuse_tracer
from src.services.opensearch.factory import make_opensearch_client
from src.services.pdf_parser.factory import make_pdf_parser_service



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the API.
    """
    logger.info("Starting RAG API...")

    settings = get_settings()
    app.state.settings = settings

    database = make_database()
    app.state.database = database
    logger.info("Database connected")

    opensearch_client = make_opensearch_client()
    app.state.opensearch_client = opensearch_client

    if opensearch_client.health_check():
        logger.info("OpenSearch connected successfully")

        setup_results = opensearch_client.setup_indices(force=False)
        if setup_results.get("hybrid_index"):
            logger.info("Hybrid index created")
        else:
            logger.info("Hybrid index already exists")

        try:
            stats = opensearch_client.client.count(index=opensearch_client.index_name)
            logger.info(f"OpenSearch ready: {stats['count']} documents indexed")
        except Exception:
            logger.info("OpenSearch index ready (stats unavailable)")
    else:
        logger.warning("OpenSearch connection failed - search features will be limited")

    app.state.arxiv_client = make_arxiv_client()
    app.state.pdf_parser = make_pdf_parser_service()
    app.state.embeddings_service = make_embeddings_service()
    app.state.ollama_client = make_ollama_client()
    app.state.langfuse_tracer = make_langfuse_tracer()
    app.state.cache_client = make_cache_client(settings)
    logger.info("Services initialized: arXiv API client, PDF parser, OpenSearch, Embeddings, Ollama, Langfuse, Cache")

    logger.info("API ready")
    yield

    database.teardown()
    logger.info("API shutdown complete")

app = FastAPI(
    name = "Arxiv Assistant",
    description= "Arxiv Assistant for Research Paper",
    version=os.getenv("APP_VERSION", "0.1.0"),
    lifespan=lifespan,
)


app.include_router(ping.router, prefix="/api/v1")  # Health check endpoint
app.include_router(hybrid_search.router, prefix="/api/v1")  # Search chunks with BM25/hybrid
app.include_router(ask_router, prefix="/api/v1")  # RAG question answering with LLM
app.include_router(stream_router, prefix="/api/v1")  # Streaming RAG responses



if __name__ =="__main__":
    uvicorn.run(app,port=8000,host="0.0.0.0")