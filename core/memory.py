class SessionMemory:
    """Simple in-memory session storage."""
    
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str) -> dict:
        """Get session data."""
        return self.sessions.get(session_id, {})

    def update(self, session_id: str, data: dict) -> None:
        """Update session data."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id].update(data)

    def clear(self, session_id: str) -> None:
        """Clear session data."""
        if session_id in self.sessions:
            del self.sessions[session_id]
