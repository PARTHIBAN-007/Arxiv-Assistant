from functools import lru_cache

from src.config import get_settings
from src.services.langfuse.client import LangfuseTracer

@lru_cache(maxsize=1)
def make_langfue_tracer()-> LangfuseTracer:
    """Create and return a singleton langfue tracer instance"""
    settings = get_settings()
    return LangfuseTracer(settings)