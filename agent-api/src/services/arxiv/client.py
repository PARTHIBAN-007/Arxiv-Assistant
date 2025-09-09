import asyncio
from loguru import logger
import time
import xml.etree.ElementTree as ET
from functools import cached_property
from pathlib import Path
from typing import Dict,List,Optional
from urllib.parse import quote,urlencode

import httpx
from src.config import ArxivSettings
from src.exceptions import ArxivAPIException, ArxivAPITimeoutError , ArxivParseError, PDFDownloadException, PDFDownloadTimeoutError
from src.schemas.arxiv.paper import ArxivPaper

class ArxivClient:
    """Client for fetching papers from arxiv API"""

    def __init__(self,settings:ArxivSettings):
        self._settings = settings
        self._last_request_time: Optional[float] = None

    @cached_property
    def pdf_cache_dir(self)->Path:
        """PDF Cache directory"""
        cache_dir = Path(self._settings.pdf_cache_dir)
        cache_dir.mkdir(parents=True,exist_ok=True)
        return cache_dir

    @property
    def base_url(self)->str:
        return self._settings.base_url
    
    @property
    def namespaces(self)->dict:
        return self._settings.namespaces
    
    @property
    def rate_limit_delay(self)->float:
        return self._settings.rate_limit_delay
    
    @property
    def timeout_seconds(self)->int:
        return self._settings.timout_seconds
    
    @property
    def max_results(self)->int:
        return self._settings.max_results
    
    @property
    def search_category(self)->str:
        return self._settings.search_category
    
    async def fetch_papers(
            self,
            max_results:Optional[int] = None,
            start: int = 0,
            sort_by: str = "submittedDate",
            sort_order: str = "descending",
            from_date: Optional[str] = None,
            to_date: Optional[str] = None,
    )-> List[ArxivPaper]:
        """
        Fetch Papers from arxiv for the configured category

        """
        if max_results is None:
            max_results = self.max_results

        search_query = f"cat:{self.search_category}"

        if from_date or to_date:
            date_from = f"{from_date}0000" if from_date else ""
            date_to = f"{to_date}2359" if to_date else ""
            search_query += f" AND SubmittedDate:[{date_from}+TO+{date_to}]"

        params = {
            "search_query": search_query,
            "start": start,
            "max_results": min(max_results,2000),
            "sortBy" : sort_by,
            "sortOrder": sort_order,
        }

        safe = ":+[]"
        url = f"{self.base_url}?{urlencode(params,quote_via=quote,safe = safe)}"

        try:
            logger.info(f"Fetching {max_results} { self.search_category} papers from arxiv")

            if self._last_request_time is not None:
                time_since_last = time.time() - self._last_request_time
                if time_since_last < self.rate_limit_delay- time_since_last:
                    sleep_time = self.rate_limit_delay - time_since_last
                    await asyncio.sleep(sleep_time)
            
            self._last_request_time = time.time()

            async with httpx.AsyncClient(timeout = self.timeout_seconds) as client:
                response = await client.get(url)
                response.raise_for_status()
                xml_data = response.text

            papers = self._parse_response(xml_data)
            logger.info(f"Fetched {len(papers)} papers")

            return papers
        
        except httpx.TimeoutException as e:
            logger.error(f"arxiv API Timeout: {e}")
            raise ArxivAPITimeoutError(f"arxiv API request timed out: {e}")
        except httpx.HTTPStausError as e:
            logger.error(f"arxiv API HTTP Error: {e}")
            raise ArxivAPIException(f"Arxiv API returned Error {e.response}")
        except Exception as e:
            logger.error(f"Failed to fetch papers from arxiv: {e}")
            raise ArxivAPIException(f"Unexpected error fetching papers from arxiv: {e}")
        
    def _parse_response(self,xml_data:str) -> List[ArxivPaper]:
        try:
            root = ET.fromstring(xml_data)
            entries = root.findall("atom:entry",self.namespaces)

            papers = []
            for entry in entries:
                paper = self._parse_single_entry(entry)
                if paper:
                    papers.append(paper)
            return paper
        except ET.ParseError as e:
            logger.error(f"Failed to parse arxiv XML Response: {e}")
            raise ArxivParseError(f"Failed to parse arxiv XML response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing arxiv response: {e}")
            raise ArxivParseError(f"Unexpected error parsing arxiv response: {e}")
    
                
    