from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger


class LLMAgent(BaseAgent):
    """General LLM agent for conversational queries."""
    
    def __init__(self):
        self.llm = OllamaLLM()
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle general conversational request."""
        query = request.user_input

        history = request.memory.get("chat_history", [])
        
        prompt = f"""
You are a helpful AI assistant. Respond to the user's message naturally and conversationally.

User: {query}

Provide a friendly, helpful response. Keep it concise and relevant.
"""
        
        try:
            response = self.llm.generate(prompt, history=history)
            
            return AgentResponse(
                status="success",
                data={"response": response},
                message=response
            )
        except Exception as e:
            logger.error(f"LLM agent error: {e}")
            return AgentResponse(
                status="error",
                message=f"Error generating response: {str(e)}"
            )
