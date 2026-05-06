# ManHas AI Assistant System - Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Tools and Technologies](#tools-and-technologies)
5. [Implementation Details](#implementation-details)
6. [Technical Decisions](#technical-decisions)
7. [Challenges and Solutions](#challenges-and-solutions)
8. [API Endpoints](#api-endpoints)
9. [Configuration](#configuration)
10. [Development Workflow](#development-workflow)

---

## System Overview

ManHas is an intelligent AI technical support assistant built with a multi-agent architecture. The system routes user queries to specialized agents based on intent classification, providing optimal responses for different types of requests.

### Key Features
- **Knowledge-based retrieval (RAG)**: Uses ChromaDB for semantic search over ingested documents
- **Code generation and execution**: Tool agent generates and validates Python code
- **Error debugging**: Debugging agent analyzes errors and provides solutions
- **Multi-turn conversation**: Maintains conversation history across sessions
- **Persistent chat storage**: JSON-based storage with auto-generated titles
- **Real-time streaming**: SSE support for streaming responses
- **Intelligent routing**: LLM-based intent classification for accurate agent selection

### System Goals
- Provide accurate technical support through specialized agents
- Ensure high-quality outputs through validation and refinement
- Maintain scalability with persistent vector storage
- Deliver responsive user experience with streaming support

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│              - Chat Interface                            │
│              - Message Display                           │
│              - Local Storage                             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/SSE
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Orchestrator)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Intent Classification (LLM-based)          │  │
│  │              Priority Routing Logic                 │  │
│  └──────────────────────────────────────────────────┘  │
│           │           │           │           │          │
│    ┌──────▼───┐ ┌────▼────┐ ┌───▼────┐ ┌───▼────┐     │
│    │   RAG    │ │  Tool   │ │ Debug  │ │  LLM   │     │
│    │  Agent   │ │  Agent  │ │ Agent  │ │ Agent  │     │
│    └──────────┘ └─────────┘ └────────┘ └────────┘     │
│           │           │           │           │          │
│    ┌──────▼───┐ ┌────▼────┐ ┌───▼────┐ ┌───▼────┐     │
│    │ ChromaDB │ │  File   │ │  N/A   │ │ Ollama │     │
│    │          │ │ System  │ │        │ │ Llama  │     │
│    └──────────┘ └─────────┘ └────────┘ └────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Query**: User sends message through React frontend
2. **HTTP Request**: Frontend sends POST to `/chat` or `/chat/stream`
3. **Orchestrator**: Backend receives request and extracts messages
4. **Intent Classification**: LLM classifies query intent (rag/tool/debug/llm)
5. **Priority Routing**: Self-referential questions routed to RAG first
6. **Agent Execution**: Query routed to appropriate agent
7. **Response Generation**: Agent processes query and generates response
8. **Validation Gate**: Response validated for quality
9. **Response Refinement**: If code present, add explanatory context
10. **Storage**: Messages saved to JSON storage
11. **Response**: Final response sent to frontend

---

## Components

### 1. Orchestrator (`orchestrator/assistant.py`)

**Purpose**: Central coordinator for all requests

**Key Functions**:
- `process_messages()`: Main entry point for processing chat messages
- `process_messages_stream()`: Streaming version for SSE
- `_route_query()`: LLM-based intent classification
- Priority routing for self-referential questions

**Intent Classification**:
- Uses LLM to classify queries into: rag, tool, debug, llm
- Priority keywords for self-referential questions:
  - "who are you", "what is your name", "your authors"
  - "according to your knowledge base"
  - "about you", "about the system"

**Validation Integration**:
- Response refinement for code-containing responses
- Quality validation before user delivery
- Automatic retry on validation failure

### 2. RAG Agent (`agents/RAG/`)

**Purpose**: Knowledge-based retrieval using vector search

**Components**:
- `RAG_agent.py`: Main agent implementation
- `chroma_retriever.py`: ChromaDB integration

**Key Features**:
- ChromaDB for persistent vector storage
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- Document chunking (300 chars, 50 overlap)
- Semantic search without query rewriting

**Ingestion Process** (`ingest_rag.py`):
1. Recursively scan `data/` directory (excluding `processed/`)
2. Load documents with progress bar
3. Chunk text into 300-character segments
4. Generate embeddings using Sentence Transformers
5. Store in ChromaDB
6. Move processed files to `data/processed/`

### 3. Tool Execution Agent (`agents/tool_execution/tool_agent.py`)

**Purpose**: Execute file operations and generate code

**Available Tools**:
- `read_file`: Read file contents
- `write_file`: Write content to file
- `list_files`: List directory contents
- `run_command`: Execute shell commands
- `search_files`: Search text in files
- `write_code`: Generate and validate Python code

**Code Generation Process**:
1. LLM generates code based on user request
2. Syntax validation using Python's `compile()`
3. If invalid, LLM fixes code (3 attempts max)
4. Returns only code block (no execution output)

**Key Optimizations**:
- JSON parsing with markdown code block handling
- Argument name mapping for flexibility
- Retry loop with LLM-based fixing
- Proper formatting prompts (PEP 8, docstrings)

### 4. Debugging Agent (`agents/debugging/debug_agent.py`)

**Purpose**: Analyze errors and provide troubleshooting guidance

**Process**:
1. Accept error message and optional code
2. Construct prompt with error context
3. LLM provides:
   - Root cause analysis
   - Step-by-step solution
   - Code fix suggestions
   - Prevention tips

### 5. Validation Gate (`agents/validation/validation_gate.py`)

**Purpose**: Ensure output quality and user-friendliness

**Validation Criteria**:
- Helpful and relevant
- Factually accurate
- Safe and appropriate
- Clear and well-structured
- Complete answer
- Not just raw code

**Response Refinement**:
- Only processes responses containing code blocks (detected by ```)
- Adds:
  - Brief introduction explaining code purpose
  - Context and explanation
  - Conclusion or next steps
- Prevents meta-commentary about refinement process

### 6. Chat Storage (`storage/chat_storage.py`)

**Purpose**: Persistent multi-chat storage

**Storage Format**: JSON files in `chats/` directory

**Chat Data Structure**:
```json
{
  "id": "uuid",
  "title": "Generated title",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "messages": [
    {
      "role": "user|assistant",
      "content": "message text",
      "timestamp": "ISO timestamp"
    }
  ]
}
```

**Auto-Title Generation**:
- LLM generates concise title (max 5 words) from first user message
- Titles limited to 50 characters
- Stored with chat metadata

---

## Tools and Technologies

### Backend Framework
- **FastAPI**: Modern Python web framework
  - Automatic API documentation
  - Type hints for validation
  - Async support
  - SSE (Server-Sent Events) for streaming

### LLM Integration
- **Ollama**: Local LLM hosting
  - Model: Llama 3.2
  - Endpoints: `/api/chat`, `/api/generate`
  - Streaming and non-streaming support

### Vector Database
- **ChromaDB**: Vector storage for RAG
  - Persistent storage (no pickle)
  - Built-in metadata support
  - Cosine similarity search
  - HNSW indexing

### Text Embeddings
- **Sentence Transformers**: Text to vector conversion
  - Model: all-MiniLM-L6-v2
  - Efficient for semantic search
  - Good balance of speed/accuracy

### Document Processing
- **LangChain**: Document loading and chunking
  - Support for multiple file formats
  - Text splitters
  - Document loaders

### Python Libraries
- **tqdm**: Progress bars for long operations
- **pydantic**: Data validation and settings management
- **subprocess**: Code execution
- **hashlib**: Chat ID generation
- **json**: Chat persistence
- **pathlib**: File path handling

### Storage
- **JSON**: Chat history persistence
- **ChromaDB**: Vector embeddings
- **File System**: Code execution, document storage

### Frontend (Existing)
- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server

---

## Implementation Details

### RAG Implementation

**Document Ingestion**:
```python
# ingest_rag.py
1. Scan data/ directory recursively
2. Exclude processed/ folder
3. Load documents with progress bar
4. Chunk text (300 chars, 50 overlap)
5. Generate embeddings
6. Store in ChromaDB
7. Move files to processed/
```

**Retrieval Process**:
```python
# RAG_agent.py
1. Check document count in ChromaDB
2. Use original query (no rewriting)
3. Search with embeddings
4. Retrieve top 5 results
5. Deduplicate chunks
6. Generate answer with context
```

**Query Processing**:
- Original query used directly (rewriting removed)
- No query expansion or transformation
- Direct semantic search

### Intent Classification

**LLM-Based Classification**:
```python
prompt = """
Classify user query into: rag, tool, debug, or llm
- rag: Knowledge-based questions
- tool: File operations, code generation
- debug: Error troubleshooting
- llm: General conversation

User query: {query}

Return ONLY category name.
"""
```

**Priority Routing**:
```python
self_referential_keywords = [
    "who are you", "what is your name",
    "your authors", "according to your knowledge base"
]
if any(keyword in query_lower for keyword in keywords):
    return "rag"
```

### Code Generation

**Tool Selection**:
```python
prompt = """
Available tools:
- read_file, write_file, list_files
- run_command, search_files, write_code

User request: {query}

Return JSON: {"tool": "name", "args": {...}}
"""
```

**Syntax Validation**:
```python
# Retry loop (3 attempts)
for attempt in range(3):
    try:
        compile(code, filename, 'exec')
        return code
    except SyntaxError:
        code = ask_llm(fix_prompt)
```

### Validation Gate

**Response Refinement**:
```python
if "```" in response:
    # Contains code, add context
    prompt = """
    Add introduction, context, and conclusion
    around this code.
    """
    response = ask_llm(prompt)
```

**Quality Validation**:
```python
prompt = """
Check if response is:
- Helpful and relevant
- Factually accurate
- Safe and appropriate
- Clear and well-structured
- Complete
- Not just raw code

Return: VALID: true/false
"""
```

---

## Technical Decisions

### Why ChromaDB over FAISS?

**Decision**: ChromaDB

**Reasons**:
- **Persistent Storage**: ChromaDB persists to disk, FAISS requires pickle
- **Scalability**: Better for growing document collections
- **Metadata Support**: Built-in metadata for documents
- **Management**: Easier to manage and query
- **No Pickle Issues**: Avoids pickle serialization problems

### Why LLM-Based Intent Classification?

**Decision**: LLM classification over keyword matching

**Reasons**:
- **Accuracy**: Better understanding of query intent
- **Flexibility**: Handles ambiguous queries
- **Adaptability**: No code changes for new patterns
- **Context**: Understands semantic meaning

### Why Validation Gate?

**Decision**: Add validation before user delivery

**Reasons**:
- **Quality Assurance**: Ensures high-quality outputs
- **User Experience**: Prevents confusing responses
- **Error Prevention**: Catches issues before user sees them
- **Refinement**: Adds context to raw code

### Why Retry Loops?

**Decision**: Add retry logic for code generation

**Reasons**:
- **Self-Correction**: LLM can fix its own mistakes
- **Success Rate**: Improves code generation success
- **User Experience**: Fewer error messages
- **Learning**: System improves through retries

### Why Remove Query Rewriting?

**Decision**: Use original query directly in RAG

**Reasons**:
- **Relevance**: Rewriting caused irrelevant results
- **Simplicity**: Direct search is more predictable
- **Performance**: Faster without transformation
- **Accuracy**: Original user intent preserved

---

## Challenges and Solutions

### Challenge 1: RAG Not Finding Relevant Documents

**Problem**: Query rewriting generated irrelevant queries, leading to irrelevant search results.

**Symptoms**:
- User asked about authors, got TCP/IP documentation
- Search results unrelated to query intent

**Solution**:
- Removed query rewriting entirely
- Use original query directly for semantic search
- Simplified RAG pipeline

**Result**: Improved search relevance

### Challenge 2: Code Syntax Errors

**Problem**: LLM generated syntactically invalid Python code.

**Symptoms**:
- Indentation errors
- Missing colons
- One-liner functions without proper structure

**Solution**:
- Added syntax validation using `compile()`
- Implemented retry loop (3 attempts)
- LLM fixes its own code on failure
- Improved generation prompt with PEP 8 guidelines

**Result**: Higher success rate for valid code

### Challenge 3: Raw Code Without Context

**Problem**: Tool agent returned code blocks without explanation.

**Symptoms**:
- Users received just code
- No explanation of what code does
- Poor user experience

**Solution**:
- Added validation gate refinement
- Only processes responses with code blocks
- Adds introduction, context, and conclusion
- Prevents meta-commentary

**Result**: User-friendly code responses

### Challenge 4: Generic Chat Titles

**Problem**: All chats named "new chat" or timestamps.

**Symptoms**:
- Difficult to identify conversations
- Poor organization

**Solution**:
- LLM generates titles from first user message
- Concise titles (max 5 words, 50 chars)
- Stored with chat metadata
- Included in API responses

**Result**: Meaningful, descriptive chat titles

### Challenge 5: Meta-Commentary in Responses

**Problem**: Refinement added explanation of changes made.

**Symptoms**:
- "Here's a refined version..."
- "I removed the unnecessary explanation..."
- Users see internal process

**Solution**:
- Added prompt instruction to prevent meta-commentary
- "Return ONLY the refined response"
- "Do not include any meta-commentary"

**Result**: Clean, direct responses

### Challenge 6: Chat Title Reverting

**Problem**: Frontend set title but reverted after server response.

**Symptoms**:
- Title changed briefly then reverted
- Frontend not using backend title

**Solution**:
- Added `title` field to `/chat` endpoint response
- Added `title` field to `/chat/sync` endpoint response
- Frontend can now use backend-generated titles

**Result**: Persistent, consistent chat titles

---

## API Endpoints

### GET `/`
Health check endpoint

**Response**:
```json
{
  "status": "running",
  "message": "AI Assistant Backend is running"
}
```

### POST `/chat`
Process chat messages (non-streaming)

**Request**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your message",
      "attachments": null
    }
  ]
}
```

**Response**:
```json
{
  "reply": "Response text",
  "chat_id": "md5-hash",
  "title": "Generated title"
}
```

### POST `/chat/sync`
Sync chat messages to backend storage

**Request**:
```json
{
  "messages": [...]
}
```

**Response**:
```json
{
  "chat_id": "md5-hash",
  "title": "Generated title",
  "messages": [...]
}
```

### GET `/chat/stream`
POST `/chat/stream`
Process chat messages with streaming (SSE)

**Request**: Same as `/chat`

**Response**: Server-Sent Events stream

### GET `/chats`
List all chat sessions

**Response**:
```json
{
  "chats": [
    {
      "id": "uuid",
      "title": "Chat title",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "message_count": 5
    }
  ]
}
```

### GET `/chats/{chat_id}`
Get specific chat messages

**Response**:
```json
{
  "id": "uuid",
  "title": "Chat title",
  "messages": [...]
}
```

### DELETE `/chats/{chat_id}`
Delete a chat session

**Response**:
```json
{
  "success": true
}
```

### POST `/chats/{chat_id}/title`
Update chat title

**Request**:
```json
{
  "title": "New title"
}
```

**Response**:
```json
{
  "success": true
}
```

---

## Configuration

### Environment Variables

**Backend**:
- `OLLAMA_URL`: Ollama API URL (default: `http://localhost:11434`)
- `BACKEND_HOST`: Backend host (default: `0.0.0.0`)
- `BACKEND_PORT`: Backend port (default: `8000`)

**Frontend**:
- `VITE_CHAT_API_URL`: Backend API URL (default: `http://localhost:8000`)

### Directory Structure

```
V6/
├── agents/
│   ├── RAG/
│   │   ├── RAG_agent.py
│   │   └── chroma_retriever.py
│   ├── LLM/
│   │   └── llm.py
│   ├── tool_execution/
│   │   └── tool_agent.py
│   ├── debugging/
│   │   └── debug_agent.py
│   └── validation/
│       └── validation_gate.py
├── orchestrator/
│   └── assistant.py
├── storage/
│   └── chat_storage.py
├── data/
│   └── processed/
├── chats/
├── chroma_db/
├── temp/
├── main.py
├── ingest_rag.py
├── requirements.txt
└── frontend/
```

### Configuration Files

**requirements.txt**:
```
fastapi
uvicorn
ollama
chromadb
sentence-transformers
langchain
tqdm
pydantic
```

---

## Development Workflow

### Starting the System

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Ingest RAG Data**:
   ```bash
   # Add documents to data/
   python ingest_rag.py
   ```

4. **Start Backend**:
   ```bash
   python main.py
   ```

5. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Adding New Documents

1. Place documents in `data/` directory
2. Run ingestion script:
   ```bash
   python ingest_rag.py
   ```
3. Documents are chunked, embedded, and stored in ChromaDB
4. Processed files moved to `data/processed/`

### Clearing RAG Data

```bash
# Stop backend
# Delete ChromaDB directory
rmdir /s /q chroma_db

# Re-ingest documents
python ingest_rag.py

# Restart backend
python main.py
```

### Deleting Chats

- Via API: `DELETE /chats/{chat_id}`
- Via file system: Delete `{chat_id}.json` from `chats/` directory

### Testing

Use `TEST_SCENARIOS.md` for comprehensive testing:
- RAG retrieval
- Code generation
- File operations
- Debugging
- Multi-turn conversation
- Chat management

---

## Performance Considerations

### RAG Performance
- **Embedding Generation**: Cached by Sentence Transformers
- **Search Speed**: HNSW indexing in ChromaDB
- **Chunk Size**: 300 characters balances precision/recall

### LLM Performance
- **Streaming**: Reduces perceived latency
- **Intent Classification**: Single LLM call per request
- **Validation**: Additional LLM call only on failure

### Storage Performance
- **JSON Chats**: Fast read/write for small to medium chats
- **ChromaDB**: Optimized for vector similarity search
- **File System**: Direct access for code execution

### Scalability
- **ChromaDB**: Can be distributed for large knowledge bases
- **Load Balancing**: FastAPI supports async for concurrent requests
- **Rate Limiting**: Can be added for API protection

---

## Security Considerations

### Code Execution
- **Sandboxing**: Currently runs in same process (future: sandbox)
- **Syntax Validation**: Prevents execution of invalid code
- **Timeout**: 30-second timeout for code execution

### File Operations
- **Path Validation**: Prevents directory traversal
- **Write Restrictions**: Limited to `temp/` directory for code

### API Security
- **CORS**: Configured for frontend origin
- **Input Validation**: Pydantic models validate requests
- **Error Handling**: Generic error messages to prevent information leakage

### Future Security Enhancements
- Tool execution sandboxing
- Rate limiting
- Authentication/authorization
- Input sanitization

---

## Future Enhancements

### Planned Features
- [ ] Streaming support for RAG agent
- [ ] More sophisticated validation criteria
- [ ] Tool execution sandboxing
- [ ] Multi-modal support (images, documents)
- [ ] User feedback integration
- [ ] Advanced caching for FAQs
- [ ] Distributed ChromaDB
- [ ] Load balancing
- [ ] Rate limiting

### Potential Improvements
- [ ] Better error messages
- [ ] Conversation summarization
- [ ] Export chat history
- [ ] Voice input/output
- [ ] Real-time collaboration
- [ ] Custom agent creation
- [ ] Plugin system

---

## Summary

ManHas is a comprehensive multi-agent AI assistant system built with:
- **FastAPI** for the backend
- **Ollama/Llama 3.2** for LLM capabilities
- **ChromaDB** for vector storage
- **React** for the frontend

The system successfully implements:
- Intelligent query routing via LLM classification
- Knowledge retrieval with RAG
- Code generation with validation
- Error debugging
- Persistent chat storage
- Real-time streaming

Key achievements include migrating from pickle to ChromaDB, implementing LLM-based intent classification, adding thinking loops for code generation, and optimizing RAG search relevance through query simplification.
