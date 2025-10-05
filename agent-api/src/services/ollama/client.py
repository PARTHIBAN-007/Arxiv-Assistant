import json
from loguru import logger
from typing import Any , Dict , List , Optional

import httpx

from src.config import Settings
from src.exceptions import OllamaConnectionError , OllamaException, OllamaTimeoutError
from src.schemas.ollama import RAGResponse
from src.services.ollama.prompts import RAGPromptBuilder , ResponseParser

class OllamaClient:
    """client for interacting with ollama LLM Inference"""

    def __init__(self):
        self.base_url = Settings.ollama_host
        self.timeout = httpx.Timeout(float(Settings.ollama_timeout))
        self.prompt_builder = RAGPromptBuilder()
        self.response_parser = ResponseParser()
    
    
