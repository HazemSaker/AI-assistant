from agents.RAG.RAG_agent import RAGAgent
from agents.tool_execution.tool_agent import ToolExecutionAgent
from agents.debugging.debug_agent import DebuggingAgent
from agents.validation.validation_gate import ValidationGate
from storage.chat_storage import ChatStorage
from agents.LLM.llm import ask_llm, ask_llm_stream

class AIAssistant:
    """
    Main orchestration layer that coordinates all agents.
    Routes queries to appropriate agents and validates outputs.
    """
    
    def __init__(self, retriever=None):
        # ChromaDB handles persistence automatically, just pass through
        self.rag_agent = RAGAgent(retriever)
        self.tool_agent = ToolExecutionAgent()
        self.debug_agent = DebuggingAgent()
        self.validator = ValidationGate()
        self.storage = ChatStorage()
    
    def process_query(self, query: str, chat_id: str = None) -> dict:
        """
        Process a user query through the appropriate agent pipeline (non-streaming).
        
        Args:
            query: User's question or request
            chat_id: Optional chat ID for context
        
        Returns:
            dict with response, chat_id, and metadata
        """
        # Create new chat if none provided
        if not chat_id:
            chat_id = self.storage.create_chat()
        
        # Save user message
        self.storage.add_message(chat_id, "user", query)
        
        # Get chat history for context
        messages = self.storage.get_messages(chat_id)
        history = [{"role": m["role"], "content": m["content"]} for m in messages[:-1]]
        
        # Determine which agent to use
        agent_type = self._route_query(query)
        
        # Get response from appropriate agent
        if agent_type == "rag" and self.rag_agent:
            response = self.rag_agent.run(query, history)
        elif agent_type == "tool":
            response = self.tool_agent.run(query)
        elif agent_type == "debug":
            response = self.debug_agent.run(query)
        else:
            # Default to direct LLM
            response = ask_llm(query, history)
        
        # Validate response
        is_valid, feedback = self.validator.validate(query, response)
        
        # Improve if not valid (max 2 attempts)
        attempts = 0
        while not is_valid and attempts < 2:
            response = self.validator.improve_response(query, response, feedback)
            is_valid, feedback = self.validator.validate(query, response)
            attempts += 1
        
        # Save assistant response
        self.storage.add_message(chat_id, "assistant", response)
        
        return {
            "response": response,
            "chat_id": chat_id,
            "agent_used": agent_type,
            "validation_passed": is_valid
        }
    
    def process_query_stream(self, query: str, chat_id: str = None):
        """
        Process a user query with streaming support.
        
        Args:
            query: User's question or request
            chat_id: Optional chat ID for context
        
        Yields:
            Response chunks as they arrive
        """
        # Create new chat if none provided
        if not chat_id:
            chat_id = self.storage.create_chat()
        
        # Save user message
        self.storage.add_message(chat_id, "user", query)
        
        # Get chat history for context
        messages = self.storage.get_messages(chat_id)
        history = [{"role": m["role"], "content": m["content"]} for m in messages[:-1]]
        
        # Determine which agent to use
        agent_type = self._route_query(query)
        
        # For streaming, only use direct LLM (other agents don't support streaming yet)
        if agent_type == "llm":
            full_response = ""
            for chunk in ask_llm_stream(query, history):
                full_response += chunk
                yield chunk
            
            # Validate and save after streaming complete
            is_valid, feedback = self.validator.validate(query, full_response)
            attempts = 0
            while not is_valid and attempts < 2:
                full_response = self.validator.improve_response(query, full_response, feedback)
                is_valid, feedback = self.validator.validate(query, full_response)
                attempts += 1
            
            self.storage.add_message(chat_id, "assistant", full_response)
        else:
            # For non-streaming agents, fall back to regular processing
            result = self.process_query(query, chat_id)
            yield result["response"]
    
    def process_messages(self, messages: list) -> str:
        """
        Process messages in frontend format (messages array).
        
        Args:
            messages: List of message dicts with role and content
        
        Returns:
            Assistant's response
        """
        print(f"[Orchestrator] process_messages called with {len(messages)} messages")
        
        if not messages:
            return "No messages provided"
        
        # Get the last user message
        last_message = messages[-1]
        if last_message.get("role") != "user":
            return "Last message must be from user"
        
        query = last_message.get("content", "")
        print(f"[Orchestrator] Query: {query}")
        
        # Convert messages to history format (exclude last message)
        history = []
        for msg in messages[:-1]:
            if msg.get("role") in ["user", "assistant"]:
                history.append({
                    "role": msg.get("role"),
                    "content": msg.get("content", "")
                })
        print(f"[Orchestrator] History: {len(history)} messages")
        
        # Determine which agent to use
        agent_type = self._route_query(query)
        print(f"[Orchestrator] Agent type: {agent_type}")
        
        # Get response from appropriate agent
        print(f"[Orchestrator] Getting response from agent...")
        if agent_type == "rag" and self.rag_agent:
            response = self.rag_agent.run(query, history)
        elif agent_type == "tool":
            response = self.tool_agent.run(query)
        elif agent_type == "debug":
            response = self.debug_agent.run(query)
        else:
            # Default to direct LLM
            print(f"[Orchestrator] Calling ask_llm...")
            response = ask_llm(query, history)
            print(f"[Orchestrator] LLM response received")
        
        print(f"[Orchestrator] Response before validation: {response[:100]}...")
        
        # Refine response to add context around code
        print("[Orchestrator] Refining response...")
        response = self.validator.refine_response(query, response)
        print(f"[Orchestrator] Refined response: {response[:100]}...")
        
        # Validate the refined response
        validated = self.validator.validate(response, query)
        if not validated:
            print("[Orchestrator] Validation failed, retrying...")
            response = ask_llm(query, history)
            print(f"[Orchestrator] Retry response: {response[:100]}...")
        
        print(f"[Orchestrator] Final response ready")
        return response
    
    def process_messages_stream(self, messages: list):
        """
        Process messages in frontend format with streaming.
        
        Args:
            messages: List of message dicts with role and content
        
        Yields:
            Response chunks as they arrive
        """
        if not messages:
            yield "No messages provided"
            return
        
        # Get the last user message
        last_message = messages[-1]
        if last_message.get("role") != "user":
            yield "Last message must be from user"
            return
        
        query = last_message.get("content", "")
        
        # Convert messages to history format (exclude last message)
        history = []
        for msg in messages[:-1]:
            if msg.get("role") in ["user", "assistant"]:
                history.append({
                    "role": msg.get("role"),
                    "content": msg.get("content", "")
                })
        
        # For streaming, use direct LLM
        agent_type = self._route_query(query)
        if agent_type == "llm":
            for chunk in ask_llm_stream(query, history):
                yield chunk
        else:
            # For non-streaming agents, fall back to regular processing
            response = self.process_messages(messages)
            yield response
    
    def _route_query(self, query: str) -> str:
        """
        Determine which agent should handle the query using LLM-based intent classification.
        """
        query_lower = query.lower()
        
        # Priority: Route self-referential questions to RAG first
        self_referential_keywords = [
            "who are you", "who are u", "what are you", "what is your name",
            "your name", "your authors", "who created you", "who made you",
            "about you", "about the system", "what is manhas", "who is manhas",
            "according to your knowledge base", "from your knowledge base"
        ]
        
        if any(keyword in query_lower for keyword in self_referential_keywords):
            if self.rag_agent:
                print(f"[Orchestrator] Self-referential question detected, routing to RAG")
                return "rag"
        
        prompt = f"""
You are an intent classifier for an AI technical support assistant. Classify the user's query into one of these categories:

- rag: Knowledge-based questions requiring document retrieval (what, how, explain, who, where, when, why, information about specific topics)
- tool: Requests to execute tools or commands (run, execute, file operations, write code, list files, search)
- debug: Error debugging and troubleshooting (error, bug, fix, not working, issue, problem)
- llm: General conversation, small talk, or questions that don't fit other categories

User query: {query}

Return ONLY the category name (rag, tool, debug, or llm) with no additional text.
"""
        
        try:
            response = ask_llm(prompt).strip().lower()
            
            # Validate response
            valid_categories = ["rag", "tool", "debug", "llm"]
            if response in valid_categories:
                # Check if RAG is available
                if response == "rag" and not self.rag_agent:
                    return "llm"
                return response
            else:
                # Fallback to LLM if classification fails
                print(f"[Orchestrator] Invalid classification: {response}, defaulting to llm")
                return "llm"
        except Exception as e:
            print(f"[Orchestrator] Classification error: {e}, defaulting to llm")
            return "llm"
    
    def get_chat_history(self, chat_id: str) -> list:
        """Get message history for a chat."""
        return self.storage.get_messages(chat_id)
    
    def list_all_chats(self) -> list:
        """List all chat sessions."""
        return self.storage.list_chats()
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat session."""
        return self.storage.delete_chat(chat_id)
