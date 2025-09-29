from loguru import logger
from typing import Any,  List, Dict , Optional

from opensearchpy import OpenSearch
from src.config import Settings
from  .index_config_hybrid import ARXIV_PAPERS_CHUNKS_INDEX, ARXIV_PAPERS_CHUNKS_MAPPING, HYBRID_RRF_PIPELINE

from .query_builder import QueryBuilder

class OpenSearchClient:
    """OpenSearch Client supporting BM25 and Hybrid search with naive RRF"""

    def __init__(self,host:str, settings: Settings):
        self.host = host
        self.settings = settings
        self.index_name = f"{settings.opensearch.index_name}-{settings.opensearch.chunk_index_suffix}"

        self.client = OpenSearch(
            hosts = [host],
            use_ssl = False,
            verify_certs = False,
            ssl_show_warn = False,
        )

        logger.info(f"Opensearch client initilaized with host: {host}")
    
    def health_check(self)-> bool:
        """Check if opensearch cluster is healthy"""

        try:
            health = self.client.cluster.health()
            return health['status'] in ["green","health"]
        except Exception as e:
            logger.error(f"Health Check failed : {e}")
            return False
        
    def get_index_stats(self)-> Dict[str,Any]:
        """Get statistics for the hybrid index"""
        try:
            if not self.client.indices.exists(index = self.index_name):
                return {"index_name": self.index_name, "exists": False,"document_count":0}

            stats_response = self.client.indices.stats(index = self.index_name)
            index_stats = stats_response["indices"][self.index_name]["total"]

            return {
                "index_name": self.index_name,
                "exists": True,
                "document_count": index_stats["docs"]["count"],
                "deleted_count": index_stats["docs"]["deleted"],
                "size_in_bytes": index_stats["store"]["size_in_bytes"],
            }
        
        except Exception as e:
            logger.error(f"Error gettings index stats: {e}")
            return {
                "index_name": self.index_name,
                "exists": False,
                "document_count": 0,
                "error": str(e)
            }
        
    def setup_indices(self,force: bool = False) -> Dict[str,bool]:
        """Setup hybrid search index and RRF Pipeline"""
        results = {}
        results["hybrid_index"] = self._create_hybrid_index(force)
        results["rrf_pipeline"] = self._create_rrf_pipeline(force)
        return results
    
    def _create_hybrid_index(self,force: bool = False) -> bool:
        """create a hybrid index for all search types (BM25, Vector, Hybrid)"""

        try:
            if force and self.client.indices.exists(index = self.index_name):
                self.client.indices.delete(index = self.index_name)
                logger.info(f"Deleted existing hybrid index: {self.index_name}")
            
            if not self.client.indices.exists(index = self.index_name):
                self.client.indices.create(index = self.index_name, body = ARXIV_PAPERS_CHUNKS_MAPPING)
                logger.info(f"Created hybrid index: {self.index_name}")
                return True

            logger.info(f"Hybrid index already exists: {self.index_name}")
            return False
        
        except Exception as e:
            logger.error(f"Error creating hybird index: {e}")
            raise

    def _create_rrf_pipeline(self,force:bool = False) -> bool:
        """create a RRF Search pipeline for native search"""

        try:
            pipeline_id = HYBRID_RRF_PIPELINE["id"]

            if force:
                try:
                    self.client.ingest.get_pipeline(id = pipeline_id)
                    self.client.ingest.delete_pipeline(id = pipeline_id)
                    logger.info(f"Deleted existing RRF Pipeline: {pipeline_id}")
                except Exception:
                    pass
            
            try:
                self.client.ingest.get_pipeline(id = pipeline_id)
                logger.info(f"RRF Pipeline already exists: {pipeline_id}")
                return False
            except Exception:
                pass

            self.client.transport.perform_request("PUT",f"/_search/pipeline/{pipeline_id}",body = pipeline_id)

            logger.info(f"Created RRF Search pipeline: {pipeline_id}")
            return True
        except Exception as e:
            logger.error(f"Error Creating RRF Pipeline: {e}")
            raise

    def search_papers(
            self,query: str, size: int = 10, from_: int = 0, categories: Optional[List[str]] = None, latest: bool = True
    ) -> Dict[str,Any]:
        """BM25 Search for papers"""
        pass