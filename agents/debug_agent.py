from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger


class DebugAgent(BaseAgent):
    """Debugging agent for error analysis and troubleshooting."""
    
    def __init__(self):
        self.llm = OllamaLLM()
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle debugging request."""
        query = request.user_input
        history = request.memory.get("chat_history", [])

        prompt = f"""
You are a debugging assistant. Analyze this technical issue:

User's problem: {query}

Provide:
1. Root cause analysis
2. Step-by-step solution
3. If applicable : Code fix
4. Prevention tips

Be clear and concise. Focus only on the technical issue described.
"""

        try:
            response = self.llm.generate(prompt, history=history)
            
            return AgentResponse(
                status="success",
                data={"analysis": response},
                message=response
            )
        except Exception as e:
            logger.error(f"Debug agent error: {e}")
            return AgentResponse(
                status="error",
                message=f"Error analyzing issue: {str(e)}"
            )
