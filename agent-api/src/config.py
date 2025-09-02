from pydantic import BaseSettings

from itertools import lru_cache

class Settings(BaseSettings):
    API_KEY: str 
    MODEL_NAME: str


@lru_cache(maxsize=1)
def get_settings()->Settings:
    return Settings()