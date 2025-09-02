from loguru import logger
import os
import uvicorn
from fastapi import FastAPI
from src.config import get_settings

app = FastAPI(
    name = "Arxiv Assistant",
    description= "Arxiv Assistant for Research Paper"
)


if __name__ =="__main__":
    uvicorn.run(app,port=8000,host="0.0.0.0")