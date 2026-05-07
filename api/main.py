import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from core.orchestrator import Orchestrator
from core.base import AgentRequest
from storage.chat_storage import ChatStorage
from storage.vector_storage import VectorStorage
from agents.rag_agent import RAGAgent
from agents.tool_agent import ToolAgent
from agents.debug_agent import DebugAgent
from agents.validation_agent import ValidationAgent
from agents.llm_agent import LLMAgent
from core.config import Config
from core.logger import logger

app = FastAPI(title="MaNHaS AI Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppState:
    vector_storage: VectorStorage = None
    chat_storage: ChatStorage = None
    orchestrator: Orchestrator = None
    validation_agent: ValidationAgent = None


# Initialize components
logger.info("Initializing application components...")

state = AppState()

@app.on_event("startup")
def startup_event():
    logger.info("Initializing application components...")

    try:
        state.vector_storage = VectorStorage()
        state.chat_storage = ChatStorage()
        state.validation_agent = ValidationAgent()

        agents = {
            "rag": RAGAgent(state.vector_storage),
            "tool": ToolAgent(),
            "debug": DebugAgent(),
            "llm": LLMAgent(),
        }

        state.orchestrator = Orchestrator(agents)

        logger.info("Application initialized successfully")

    except Exception as e:
        logger.exception("Startup failed")
        raise e
    
def get_orchestrator() -> Orchestrator:
    return state.orchestrator

def get_chat_storage() -> ChatStorage:
    return state.chat_storage

def get_validation_agent() -> ValidationAgent:
    return state.validation_agent

class Message(BaseModel):
    role: str
    content: str
    attachments: Optional[List[dict]] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    chat_id: Optional[str] = None


@app.get("/")
def root():
    return {
        "status": "running", 
        "message": "MaNHaS AI Assistant is running"
    }


@app.post("/chat")
def process_chat(request: ChatRequest, 
    orchestrator: Orchestrator = Depends(get_orchestrator),
    chat_storage: ChatStorage = Depends(get_chat_storage),
    validation_agent: ValidationAgent = Depends(get_validation_agent),):
    """Process chat messages."""

    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        last_message = request.messages[-1]

        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        query = last_message.content.strip()

        if not query:
            raise HTTPException(status_code=400, detail="Empty query")

        # Generate chat_id from first message like V6
        import hashlib
        from datetime import datetime
        if request.chat_id:
            chat_id = request.chat_id
        else:
            # Generate deterministic chat_id from FIRST message content (not last)
            first_msg = request.messages[0]
            first_content = first_msg.content.strip()
            chat_id = hashlib.md5(first_content.encode()).hexdigest()
            # Check if chat exists, if not create with title
            existing_chat = chat_storage.get_chat(chat_id)
            if not existing_chat:
                # Manually create chat with the MD5 hash as ID
                chat_data = {
                    "id": chat_id,
                    "title": first_content[:50] + "..." if len(first_content) > 50 else first_content,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "messages": []
                }
                chat_storage._save_chat(chat_id, chat_data)

        # Save all messages to storage (like V6)
        messages_dict = [msg.model_dump() for msg in request.messages]
        for msg in messages_dict:
            chat_storage.add_message(chat_id, msg.get("role"), msg.get("content"))

        # Create request for orchestrator
        agent_request = AgentRequest(
            user_input=query,
            session_id=chat_id,
            memory={
                "chat_history":""
            }
        )
        
        MAX_ITERATIONS = Config.MAX_RETRIES
        threshold = Config.THRESHOLD
        best_response = None
        best_validation = {}
        best_score = -1

        for i in range(MAX_ITERATIONS):
            history = chat_storage.get_chat(chat_id)["messages"]

            # Pass history as list of dictionaries (exclude current user message)
            chat_history = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]
            agent_request.memory["chat_history"] = chat_history

             # Route and process
            response = orchestrator.handle(agent_request)

            chat_storage.add_message(chat_id, "assistant", response.message)
            if response is None:
                raise HTTPException(status_code=500, detail="No response generated")

            # Refine response if it contains code
            validation_result = validation_agent.validate(query, response.message)
            scores = validation_result.get("scores", {})
            valid_scores = [
                float(v) for v in scores.values()
                if isinstance(v, (int, float, str)) and str(v).isdigit()
            ]

            if not valid_scores:
                logger.warning("No valid scores returned")
                avg_score = 0
            else:
                avg_score = sum(valid_scores) / len(valid_scores)

            is_valid = validation_result.get("is_valid", False) or (avg_score >= threshold)

            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)
                is_valid = avg_score >= threshold
                logger.info(f"avg validation scores for the request : {avg_score}")
            else:
                avg_score = 0
                is_valid = False
            
            if avg_score > best_score:
                best_score = avg_score
                best_response = response.message
                best_validation = validation_result

            if is_valid:
                break

            agent_request = AgentRequest(
                user_input=query,
                session_id=chat_id,
                memory={
                    "chat_history": chat_history,
                    "previous_attempt": best_response or response.message,
                    "feedback": validation_result.get("feedback", ""),
                    "iteration": i,
                    "goal": "Improve answer using feedback"
                }
            )
            best_response = best_response or response.message

        reply = best_response
        final_validation = best_validation
            
        # Save to chat storage
        chat_storage.add_message(chat_id, "user", query)
        chat_storage.add_message(chat_id, "assistant", reply)

        return {
            "reply": reply,
            "chat_id": chat_id,
            "title": chat_storage.get_chat(chat_id).get("title"),
            "iterations": i + 1,
            "final_validation": final_validation,
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chats")
def list_chats(chat_storage : ChatStorage = Depends(get_chat_storage)):
    """List all chat sessions."""
    try:
        chats = chat_storage.list_chats()
        return {"chats": chats}
    
    except Exception as e:
        logger.error(f"Error listing chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chats/{chat_id}")
def get_chat(chat_id: str, chat_storage: ChatStorage = Depends(get_chat_storage)):
    """Get a specific chat."""
    try:
        chat = chat_storage.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, chat_storage: ChatStorage = Depends(get_chat_storage)):
    """Delete a chat."""
    try:
        success = chat_storage.delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)
