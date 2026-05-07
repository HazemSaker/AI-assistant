from typing import Optional, Dict, Any

class AgentRequest:
    """Base request object for all agents."""
    
    def __init__(
        self,
        user_input: str,
        session_id: str,
        memory: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ):
        self.user_input = user_input
        self.session_id = session_id
        self.memory = memory or {}
        self.metadata = metadata or {}


class AgentResponse:
    """Base response object for all agents."""
    
    def __init__(
        self,
        status: str,
        data: Optional[Dict] = None,
        message: Optional[str] = None,
        next_action: Optional[str] = None,
        meta: Optional[Dict] = None,
    ):
        self.status = status 
        self.data = data or {}
        self.message = message
        self.next_action = next_action
        self.meta = meta or {}

    def __repr__(self):
        return f"<AgentResponse status={self.status}>"


class BaseAgent:
    """Base class for all agents."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Process the request and return a response."""
        raise NotImplementedError
