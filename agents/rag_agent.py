from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger
from storage.vector_storage import VectorStorage


class RAGAgent(BaseAgent):
    """Retrieval-Augmented Generation agent."""
    
    def __init__(self, vector_storage: VectorStorage = None):
        self.llm = OllamaLLM()
        self.vector_storage = vector_storage or VectorStorage()
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle RAG query."""
        query = request.user_input
        history = request.memory.get("chat_history", [])

        # Check if we have documents
        if self.vector_storage.count() == 0:
            return AgentResponse(
                status="error",
                message="No documents in knowledge base. Add documents to data/ directory."
            )

        # Retrieve relevant context
        context = self.vector_storage.search(query)

        if not context:
            return AgentResponse(
                status="error",
                message="No relevant information found in knowledge base."
            )

        # Generate answer with context
        answer = self.generate_answer(query, context, history)

        return AgentResponse(
            status="success",
            data={"context": context},
            message=answer
        )

    def generate_answer(self, query: str, context: list, history: list) -> str:
        """Generate answer from retrieved context."""
        context_text = "\n\n".join(context)

        prompt = f"""
You are a helpful AI assistant for technical support and developers.
Answer the question based on the context below.

Context:
{context_text}

Question: {query}

Provide a clear, accurate answer based only on the context.
"""

        return self.llm.generate(prompt, history=history)
