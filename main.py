from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from orchestrator.assistant import AIAssistant

app = FastAPI(title="AI Assistant Backend")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant
assistant = AIAssistant(retriever=None)

class Message(BaseModel):
    role: str
    content: str
    attachments: Optional[List[dict]] = None

class ChatRequest(BaseModel):
    messages: List[Message]

class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None

class ChatTitleRequest(BaseModel):
    chat_id: str
    title: str

@app.get("/")
def root():
    return {"status": "running", "message": "AI Assistant Backend is running"}

@app.post("/chat")
def process_chat(request: ChatRequest):
    """
    Process chat messages in frontend format.
    Accepts: { messages: [{ role, content, attachments? }] }
    Returns: { reply: string, chat_id: string, title: string }
    """
    try:
        print(f"Received request with {len(request.messages)} messages")
        messages_dict = [msg.model_dump() for msg in request.messages]
        print(f"Processing messages: {messages_dict}")
        
        # Generate or get chat_id from first message
        if messages_dict:
            first_msg = messages_dict[0]
            import hashlib
            chat_id = hashlib.md5(first_msg.get("content", "").encode()).hexdigest()
            
            # Check if chat exists, if not create with title
            existing_chat = assistant.storage.get_chat(chat_id)
            if not existing_chat:
                # Generate title from first user message
                first_user_msg = None
                for msg in messages_dict:
                    if msg.get("role") == "user":
                        first_user_msg = msg.get("content", "")
                        break
                
                if first_user_msg:
                    from agents.LLM.llm import ask_llm
                    title_prompt = f"""
Generate a concise title (max 5 words) for this chat based on the first user message.
User message: {first_user_msg}

Return ONLY the title, no additional text.
"""
                    generated_title = ask_llm(title_prompt).strip().strip('"').strip("'")
                    if len(generated_title) > 50:
                        generated_title = generated_title[:50] + "..."
                    assistant.storage.create_chat(title=generated_title)
                else:
                    assistant.storage.create_chat()
        else:
            chat_id = assistant.storage.create_chat()
        
        # Save messages to storage
        for msg in messages_dict:
            assistant.storage.add_message(chat_id, msg.get("role"), msg.get("content"))
        
        response = assistant.process_messages(messages_dict)
        print(f"Response: {response[:100]}...")
        
        # Get chat data for title
        chat_data = assistant.storage.get_chat(chat_id)
        return {
            "reply": response,
            "chat_id": chat_id,
            "title": chat_data.get("title") if chat_data else None
        }
    except Exception as e:
        import traceback
        print(f"Error processing chat: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/sync")
def sync_chat(request: ChatRequest):
    """
    Sync chat messages to backend storage.
    Accepts: { messages: [{ role, content, attachments? }] }
    Returns: { chat_id: string, messages: list }
    """
    try:
        messages_dict = [msg.model_dump() for msg in request.messages]
        
        # Create or get chat based on first message content as ID
        if messages_dict:
            first_msg = messages_dict[0]
            import hashlib
            chat_id = hashlib.md5(first_msg.get("content", "").encode()).hexdigest()
            
            # Check if chat exists
            existing_chat = assistant.storage.get_chat(chat_id)
            if not existing_chat:
                # New chat - generate title from first user message
                first_user_msg = None
                for msg in messages_dict:
                    if msg.get("role") == "user":
                        first_user_msg = msg.get("content", "")
                        break
                
                if first_user_msg:
                    # Generate concise title using LLM
                    from agents.LLM.llm import ask_llm
                    title_prompt = f"""
Generate a concise title (max 5 words) for this chat based on the first user message.
User message: {first_user_msg}

Return ONLY the title, no additional text.
"""
                    generated_title = ask_llm(title_prompt).strip().strip('"').strip("'")
                    # Limit title length
                    if len(generated_title) > 50:
                        generated_title = generated_title[:50] + "..."
                    chat_id = assistant.storage.create_chat(title=generated_title)
                else:
                    chat_id = assistant.storage.create_chat()
        else:
            chat_id = assistant.storage.create_chat()
        
        # Save all messages
        for msg in messages_dict:
            assistant.storage.add_message(chat_id, msg.get("role"), msg.get("content"))
        
        # Get chat data to include title
        chat_data = assistant.storage.get_chat(chat_id)
        return {
            "chat_id": chat_id,
            "title": chat_data.get("title") if chat_data else None,
            "messages": assistant.storage.get_messages(chat_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
@app.get("/chat/stream")
def process_chat_stream(request: ChatRequest = None, messages: str = None):
    """
    Process chat messages with streaming support.
    Accepts: { messages: [{ role, content, attachments? }] }
    Returns: Server-Sent Events stream
    """
    try:
        # Handle both POST (body) and GET (query param)
        if request and hasattr(request, 'messages') and request.messages:
            messages_dict = [msg.dict() for msg in request.messages]
        elif messages:
            # Parse from query param (JSON string)
            import json
            messages_dict = json.loads(messages)
        else:
            raise HTTPException(status_code=400, detail="No messages provided. Use POST with JSON body or GET with ?messages=...")
        
        def generate():
            for chunk in assistant.process_messages_stream(messages_dict):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        import traceback
        print(f"Error in stream: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def process_query(request: QueryRequest):
    """Process a user query (legacy endpoint)."""
    try:
        result = assistant.process_query(request.query, request.chat_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats")
def list_chats():
    """List all chat sessions."""
    try:
        chats = assistant.list_all_chats()
        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    """Get a specific chat and its messages."""
    try:
        messages = assistant.get_chat_history(chat_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"chat_id": chat_id, "messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    """Delete a chat session."""
    try:
        success = assistant.delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chats/title")
def update_chat_title(request: ChatTitleRequest):
    """Update chat title."""
    try:
        success = assistant.storage.update_chat_title(request.chat_id, request.title)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Title updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
