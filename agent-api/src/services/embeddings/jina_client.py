from typing import List
from loguru import logger
import httpx

from src.schemas.embeddings.jina import JinaEmbeddingRequest, JinaEmbeddingResponse


class JinaEmbeddingsClient:
    def __init__(self,api_key:str,base_url:str = "https://api.jina.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(timeout = 30.0)
        logger.info("Jina Embeddings Client Initialized")
    
    async def embed_chunks(self,chunks:List[str], batch_size: int = 100) -> List[List[float]]:
        embeddings = []
        
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+1]

            request_data  = JinaEmbeddingRequest(
                model="jina-embeddings-v3", task="retrieval.passage", dimensions=1024, input=batch
            )

            try:
                response = await self.client.post(
                    f"{self.base_url}/embeddings",headers=self.headers,json = request_data.model_dump()
                )
                response.raise_for_status()
                result = JinaEmbeddingResponse(**response.json())
                batch_embeddings = [item["embedding"] for item in result.data]
                embeddings.extend(batch_embeddings)

                logger.debug(f"Embedded Batch of {len(batch)}")
            
            except httpx.HTTPError as e:
                logger.error(f"Error Embedding Chunk : {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected Error Embedding Chunk : {e}")
                raise

        


    async def embed_query(self,query:str)->List[float]:
        request_data = JinaEmbeddingRequest(model="jina-embeddings-v3", task="retrieval.query", dimensions=1024, input=[query])
        try:
            response = await self.client.post(f"{self.base_url}/embeddings",headers = self.headers,json = request_data.model_dump())

            response.raise_for_status()

            result = JinaEmbeddingResponse(**response.json())
            embedding = result.data[0]['embedding']

            logger.debug(f"Embed Query: {query[:50]}...")
            return embedding
        except httpx.HTTPError as e:
            logger.error(f"Error Embedding Query : {e}")
        except Exception as e:
            logger.error(f"Unexpected Error in Embed Query: {e}")
        
    async def close(self):
        await self.client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await self.close()        
