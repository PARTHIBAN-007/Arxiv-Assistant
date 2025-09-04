from typing import Optional
from src.config import Settings, get_settings
from .jina_client import JinaEmbeddingsClient


def get_embedding_service(settings:Optional[Settings] = None) -> JinaEmbeddingsClient:
    if settings is None:
        settings = get_settings()

    jina_api_key = settings.jina_api_key

    return JinaEmbeddingsClient(api_key = jina_api_key)


def get_embedding_client(settings:Optional[Settings] = None) -> JinaEmbeddingsClient:
    if settings is None:
        settings = get_settings()

    jina_api_key = settings.jina_api_key

    return JinaEmbeddingsClient(api_key = jina_api_key)