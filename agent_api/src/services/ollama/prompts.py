import json
import re
from pathlib import Path
from typing import Any,  Dict, List
from pydantic import ValidationError

from src.schemas.ollama import RAGResponse

class RAGPromptBuilder:
    """Prompt Class for creating RAG Prompts"""

    def __init__(self):
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self):
        prompt = """
                You are an AI assistant specialized in answering questions about academic papers from arXiv. Your task is to provide accurate, helpful answers based ONLY on the provided paper excerpts.

                CRITICAL: Do NOT add any introductory text, explanations, or formatting comments like "Here's the answer" or "Here's the JSON".

                Instructions:
                1. Base your answer STRICTLY on the provided paper excerpts
                2. If the excerpts don't contain enough information to answer the question, say so clearly
                3. Cite the specific papers (by title or arXiv ID) when providing information
                4. Be concise but comprehensive in your response - LIMIT YOUR RESPONSE TO 300 WORDS MAXIMUM
                5. Maintain academic accuracy and precision
                6. If multiple papers discuss the topic, synthesize the information coherently
                7. Use direct quotes from the chunks when particularly relevant
                8. Structure your answer logically with clear paragraphs when appropriate
                9. Keep it less than 200 words

                Remember:
                - Do NOT make up information not present in the excerpts
                - Do NOT use knowledge beyond what's provided in the paper excerpts
                - Always acknowledge uncertainty when the excerpts are ambiguous or incomplete
                - Prioritize relevance and clarity in your response
                - NEVER add introductory phrases or explanations before your JSON response
            """
        return prompt
    
    def create_rag_prompt(self, query: str, chunks: List[Dict[str,Any]])->str:
        """Create a RAG Prompt with query and retrieved chunks"""
        prompt = f"{self.system_prompt}\n\n"
        prompt += "### context from papers: \n\n"

        for i,chunk in enumerate(chunks,1):
            chunk_text = chunk.get("chunk_text",chunk.get("content",""))
            arxiv_id = chunk.get("arxiv_id","")

            prompt += f"[{i}. arxiv: {arxiv_id}]\n"
            prompt += (
                "###Answer: \n Provide a natural, conversational response(not Json) and cire sources using [arxiv:id] format .\n"

            )

        return prompt
    
    def create_structured_prompt(self,query:str , chunks: List[Dict[str,Any]])-> Dict[str,Any]:
        """Prompt for ollama structured output"""
        prompt_text = self.create_rag_prompt(query,chunks)

        return {
            "prompt": prompt_text,
            "format": RAGResponse.model_json_scheme(),
        }        
    
class ResponseParser:
    """Parse LLM Response"""

    @staticmethod
    def parse_structured_response(response: str) -> Dict[str,Any]:
        """Parse strcutured response from Ollama"""
        try:
            parsed_json = json.loads(response)
            validated_response = RAGResponse(**parsed_json)
            return validated_response.model_dump()
        except (json.JSONDecodeError, ValidationError):
            return ResponseParser._extract_json_fallback(response)
        
    @staticmethod
    def _extract_json_fallback(response:str)-> Dict[str,Any]:
        """Extract Json from response text as fallback"""
        json_match = re.search(r"\{.*\}",response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                validated = RAGResponse(**parsed)
                return validated.model_dump()
            except (json.JSONDecodeError,ValidationError):
                pass

        return {
            "answer": response,
            "sources": [],
            "confidence": "low",
            "citations": [],
        }

        


