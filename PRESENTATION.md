# ManHas AI Assistant System Presentation
## Architecture, Implementation, and Tools Overview

---

## Slide 1: System Overview

**ManHas** - Intelligent AI Technical Support Assistant

A multi-agent AI system designed to provide technical support through:
- Knowledge-based retrieval (RAG)
- Code generation and execution
- Error debugging and troubleshooting
- Multi-turn conversation support
- Persistent chat storage

**Key Goal**: Route user queries intelligently to specialized agents for optimal responses

---

## Slide 2: System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│              - Chat Interface                            │
│              - Message Display                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/SSE
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Orchestrator)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Intent Classification (LLM-based)          │  │
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

---

## Slide 3: Core Components

### 1. **Orchestrator** (`orchestrator/assistant.py`)
- Central coordinator for all requests
- LLM-based intent classification for routing
- Validation gate for output quality
- Response refinement for user-friendly output

### 2. **RAG Agent** (`agents/RAG/`)
- ChromaDB-based vector storage
- Semantic search with sentence transformers
- Document chunking and embedding
- Knowledge base retrieval

### 3. **Tool Execution Agent** (`agents/tool_execution/`)
- File operations (read, write, list)
- Command execution
- Code generation with syntax validation
- Retry loop with LLM-based fixing

### 4. **Debugging Agent** (`agents/debugging/`)
- Error analysis and root cause identification
- Step-by-step troubleshooting guidance
- Code fix suggestions

### 5. **Validation Gate** (`agents/validation/`)
- Response quality validation
- Code refinement for context
- Meta-commentary prevention

---

## Slide 4: Implementation Progress

### ✅ Completed Features

| Feature | Status | Notes |
|---------|--------|-------|
| RAG Data Ingestion | ✅ | ChromaDB, progress bar, file movement |
| Chat Storage | ✅ | JSON-based, multi-chat support |
| Intent Classification | ✅ | LLM-based routing |
| Tool Execution | ✅ | JSON parsing, syntax validation, retry loop |
| Debugging Agent | ✅ | Error analysis |
| Validation Gate | ✅ | Quality check, response refinement |
| Auto Chat Titles | ✅ | LLM-generated from first message |
| Priority Routing | ✅ | Self-referential questions → RAG |
| SSE Streaming | ✅ | Real-time responses |

### 🔧 Optimizations Applied

- Removed query rewriting in RAG (was causing irrelevant results)
- Added priority routing for identity questions
- Syntax validation with LLM-based retry for code
- Response refinement only for code-containing responses
- Meta-commentary prevention in refined outputs

---

## Slide 5: Approaches & Methodologies

### 1. **Multi-Agent Architecture**
- Specialized agents for different query types
- Orchestrator routes based on intent
- Each agent optimized for its domain

### 2. **LLM-Based Intent Classification**
- Replaced keyword matching with semantic understanding
- More accurate routing decisions
- Adaptable to new query patterns

### 3. **RAG with ChromaDB**
- Vector embeddings for semantic search
- Persistent storage (no pickle)
- Scalable document management

### 4. **Validation Gate Pattern**
- Quality assurance before user delivery
- Automatic retry on failure
- Response refinement for better UX

### 5. **Thinking Loops**
- Code generation: Syntax validation → LLM fix → Retry
- Validation: Check → Refine → Validate again
- Ensures high-quality outputs

---

## Slide 6: Tools & Technologies

### Backend
- **FastAPI**: Web framework, SSE streaming
- **Ollama**: LLM hosting (Llama 3.2)
- **ChromaDB**: Vector database for RAG
- **Sentence Transformers**: Text embeddings (all-MiniLM-L6-v2)

### Python Libraries
- **langchain**: Document loading, chunking
- **tqdm**: Progress bars
- **pydantic**: Data validation

### Storage
- **JSON**: Chat persistence
- **ChromaDB**: Vector embeddings
- **File System**: Code execution, document storage

### Frontend (Existing)
- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool

---

## Slide 7: Key Technical Decisions

### Why ChromaDB over FAISS?
- Persistent storage (no pickle files)
- Better scalability
- Built-in metadata support
- Easier management

### Why LLM-based Intent Classification?
- More accurate than keyword matching
- Handles ambiguous queries better
- Adaptable without code changes

### Why Validation Gate?
- Ensures output quality
- Prevents raw code without context
- Catches errors before user sees them

### Why Retry Loops?
- Code syntax errors are common
- LLM can self-correct
- Improves success rate

---

## Slide 8: Data Flow

```
User Query
    ↓
Frontend (React)
    ↓ HTTP POST /chat
FastAPI Backend
    ↓
Orchestrator
    ↓
Intent Classification (LLM)
    ↓
┌────────┬────────┬────────┬────────┐
│  RAG   │  Tool  │ Debug  │  LLM   │
└────────┴────────┴────────┴────────┘
    ↓
Validation Gate
    ↓ (if invalid)
Retry with LLM
    ↓
Response Refinement (if code)
    ↓
Frontend Display
```

---

## Slide 9: Current Challenges & Solutions

### Challenge 1: RAG Not Finding Relevant Documents
**Problem**: Query rewriting caused irrelevant search results
**Solution**: Removed rewriting, use original query directly

### Challenge 2: Code Syntax Errors
**Problem**: LLM generates invalid code
**Solution**: Retry loop with LLM-based fixing (3 attempts)

### Challenge 3: Raw Code Without Context
**Problem**: Tool agent returned just code blocks
**Solution**: Validation gate adds explanatory text

### Challenge 4: Generic Chat Titles
**Problem**: All chats named "new chat"
**Solution**: LLM generates titles from first message

### Challenge 5: Meta-Commentary in Responses
**Problem**: Refinement added explanation of changes
**Solution**: Prompt instruction to prevent meta-commentary

---

## Slide 10: Future Enhancements

### Potential Improvements
- [ ] Streaming for RAG agent (currently non-streaming)
- [ ] More sophisticated validation criteria
- [ ] Tool execution sandboxing for security
- [ ] Multi-modal support (images, documents)
- [ ] User feedback integration for learning
- [ ] Advanced caching for frequently asked questions

### Scalability Considerations
- Distributed ChromaDB for large knowledge bases
- Load balancing for multiple concurrent users
- Rate limiting for API endpoints

---

## Slide 11: Summary

**ManHas System Highlights:**

- ✅ Multi-agent architecture with intelligent routing
- ✅ RAG with ChromaDB for knowledge retrieval
- ✅ Tool execution with syntax validation
- ✅ Validation gate for quality assurance
- ✅ Persistent chat storage with auto-titling
- ✅ Real-time streaming support
- ✅ Comprehensive error handling and retry logic

**Key Achievements:**
- Successfully migrated from pickle to ChromaDB
- Implemented LLM-based intent classification
- Added thinking loops for code generation
- Optimized RAG search relevance
- Improved user experience with refined responses

---

## Slide 12: Q&A

**Thank You!**

Questions about:
- System architecture?
- Implementation details?
- Tools and technologies?
- Future enhancements?
