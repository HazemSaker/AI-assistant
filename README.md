# AI Assistant Backend

Backend for intelligent technical support AI assistant using Llama3.2 via Ollama.

## Architecture

### Agents
- **RAG Agent**: Retrieval-augmented generation for knowledge-based questions
- **Tool Execution Agent**: Executes file operations and shell commands
- **Debugging Agent**: Analyzes errors and provides debugging solutions
- **Validation Gate**: Ensures all outputs are safe, accurate, and helpful

### Components
- **LLM Module**: Interfaces with Ollama (Llama3.2)
- **Chat Storage**: JSON-based multi-chat session management
- **Orchestrator**: Routes queries to appropriate agents

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install and run Ollama:
```bash
# Download Ollama from https://ollama.com
# Pull Llama3.2 model
ollama pull llama3.2
# Start Ollama server
ollama serve
```

3. Run the backend:
```bash
python main.py
```

Server will start on `http://localhost:8000`

## API Endpoints

### Main Chat Endpoints (Frontend Compatible)
- `POST /chat` - Process chat messages (non-streaming)
  - Request: `{ messages: [{ role, content, attachments? }] }`
  - Response: `{ reply: string }`
- `POST /chat/stream` - Process chat messages with streaming (SSE)
  - Request: `{ messages: [{ role, content, attachments? }] }`
  - Response: Server-Sent Events stream with chunks

### Legacy Endpoints
- `POST /query` - Process a user query (legacy)
- `GET /chats` - List all chat sessions
- `GET /chats/{chat_id}` - Get chat messages
- `DELETE /chats/{chat_id}` - Delete a chat
- `POST /chats/title` - Update chat title

## Example Usage

### Non-streaming (compatible with frontend):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "How do I fix a Python import error?"}]}'
```

### Streaming (real-time):
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Explain quantum computing"}]}'
```

## Project Structure

```
V6/
├── agents/
│   ├── LLM/          # Ollama interface
│   ├── RAG/          # Retrieval-augmented generation
│   ├── tool_execution/  # File/command execution
│   ├── debugging/    # Code debugging
│   ├── validation/   # Output quality gate
│   └── speech/       # Speech-to-text
├── storage/          # Chat history management
├── orchestrator/     # Agent coordination
├── main.py          # FastAPI server
└── requirements.txt
```
