from loguru import logger

from sqlalchemy import text

from .common import get_cached_services

def setup_environment():
    """Setup environment and verify dependencies"""

    logger.info("Setting up env for arxiv paper ingestion")

    try:
        arxiv_client , _pdf_parser ,database,  _metadata_fetcher , opensearch_client = get_cached_services()

        with database.get_session() as session:
            session.execute(text("SELECT 1"))
            logger.info("Database connection verified")

        try:
            health = opensearch_client.client.cluster.health():
            if health["status"] in ["green","yellow","red"]:
                logger.info(f"Opensearch hybrid client connected cluster status: {health["status"]}")
            else:
                raise Exception(f"Opensearch cluster unhealthy {health['status']}")
        except Exception as e:
            raise Exception(f"Opensearch hybrid client connection failed")

        setup_results = opensearch_client.setup_indices(force= False)           
        if setup_results.get("hybrid_index"):
            logger.info("Hybrid search index created with vector support")
        else:
            logger.info("Hybrid search index already exists")
        

        if setup_results.get("rrf_pipeline"):
            logger.info("RRF pipeline created successfully")
        else:
            logger.info("RRF Pipeline already exists")

        logger.info("Hybrid search setup completed")

        logger.info(f"Arxiv client ready: {arxiv_client.base_url}")
        logger.info("PDF Parser service readt - Docling Models")

        return {"status":"success","message": "Environment setup completed"}
    
    except Exception as e:
        error_msg = f"Environment setup failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)