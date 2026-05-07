import json
from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger


class Orchestrator(BaseAgent):
    """Routes queries to appropriate agents based on intent."""
    
    def __init__(self, agents: dict):
        self.agents = agents
        self.llm = OllamaLLM()

    def handle(self, request: AgentRequest) -> AgentResponse:
        """Route request to appropriate agent."""
        intent = self.detect_intent(request)
        logger.info(f"Intent detected: {intent}")
        
        agent = self.route(intent)
        response = agent.handle(request)
        
        return response

    def route(self, intent: str):
        """Route to agent based on intent."""
        if intent == "rag" and "rag" in self.agents:
            return self.agents["rag"]
        if intent == "tool" and "tool" in self.agents:
            return self.agents["tool"]
        if intent == "debug" and "debug" in self.agents:
            return self.agents["debug"]

        return self.agents.get("llm", self.agents.get("debug"))

    def detect_intent(self, request: AgentRequest) -> str:
        """Detect intent using LLM classification."""
        text = request.user_input.lower()
        
        # Priority routing for self-referential questions
        self_referential = [
            "who are you", "what is your name", "your authors",
            "about you", "about the system", "what is manhas"
        ]
        if any(kw in text for kw in self_referential):
            return "rag"

        # LLM-based classification for ambiguous queries
        system_prompt = """
You are an intent classifier for the MaNHaS AI system. 
Classify the user query into EXACTLY one of these categories:

- rag: Technical documentation, system-specific info, or explaining concepts ("What is...", "How does MaNHaS...")
- tool: Requests to write, execute, or manage code and files ("Write a script", "Run this", "Save to...")
- debug: Analyzing errors, fixing bugs, or troubleshooting ("I got an error", "Why is this crashing?")
- llm: Greetings, small talk, and general non-technical questions ("Hi", "Who made you?")

Rules:
1. If multiple intents are present, prioritize technical actions over greetings.
2. Return ONLY the lowercase word: rag, tool, debug, or llm.

Examples:
"Hi, can you fix my indentation error?" -> debug
"How do I open a file?" -> llm
"Explain the MaNHaS architecture." -> rag
"Generate a script to ping a server." -> tool
"""
        
        try:
            response = self.llm.generate(
                prompt=request.user_input,
                system=system_prompt
            )
            intent = response.strip().lower()
            
            valid = ["rag", "tool", "debug", "llm"]
            if intent in valid:
                return intent
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
        
        return "llm"
