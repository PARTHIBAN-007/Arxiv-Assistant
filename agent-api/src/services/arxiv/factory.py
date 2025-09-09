from src.config import get_settings

from .client import ArxivClient


def make_arxiv_client()-> ArxivClient:
    """
    Factory function to create an Arxiv Client instance
    """
    settings = get_settings
    client = ArxivClient()
    return client