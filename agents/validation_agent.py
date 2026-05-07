from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger
import json
import re


class ValidationAgent(BaseAgent):
    """Validation gate for response quality and refinement."""
    
    def __init__(self):
        self.llm = OllamaLLM()
        self.threshold = 4.0
    
    def validate(self, query: str, response: str) -> dict:
        """Validate if response is ready for user."""
        prompt = f"""
Act as a Quality Assurance Engineer for an AI Technical Support system.
Evaluate the following response based on the user's question.

Question: {query}
Response: {response}

Score the response from 1 to 5 on these metrics:
1. Relevance: Does it answer the specific question asked?
2. Clarity: Is the explanation easy to follow?
3. Completeness: Are there missing steps or context?
4. Technical Accuracy: Is the code/logic sound?

Return ONLY a JSON object:
{{
    "scores": {{"relevance": 0 - 5, "clarity": 0 - 5, "completeness": 0 - 5, "accuracy": 0 - 5}},
    "is_valid": true/false,
    "feedback": "Specific reason if any score is below {self.threshold}"
}}
"""
        
        result = self.llm.generate(prompt)
        
        try:
            return self.extract_json(result)

        except Exception:
            logger.error(f"Validation parse failed: {result}")
            return {
            "scores": {
                "relevance": 3,
                "clarity": 3,
                "completeness": 3,
                "accuracy": 3
            },
            "is_valid": True,
            "feedback": "Fallback validation used"
        }
        
    def refine_response(self, query: str, response: str, feedback: str) -> str:
        """Refine response to add context around code."""
        
        prompt = f"""
        The previous response was flagged for improvement.
        
        User Question: {query}
        Original Response: {response}
        Critique: {feedback}

        Task: Rewrite the response to address the critique while keeping any code blocks intact.
        Ensure the output is professional, helpful, and technically precise.
        """
        
        return self.llm.generate(prompt)

    def extract_json(self, text: str):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("No JSON found")
            return json.loads(text[start:end+1])