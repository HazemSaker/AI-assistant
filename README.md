# MaNHaS - Machine Learning and Human Assistive System

MaNHaS is a multi-agent AI technical support assistant built with local LLMs (Ollama Llama3.2) and vector databases (ChromaDB). It features intent classification, RAG (Retrieval-Augmented Generation), tool execution, debugging, and speech-to-text capabilities.

## Features

- **Multi-Agent Architecture**: Orchestrator routes queries to specialized agents (RAG, Tool, Debug, LLM, Speech)
- **Local LLM**: Uses Ollama Llama3.2 for all text generation (no API keys required)
- **RAG with ChromaDB**: Document retrieval and answer generation from knowledge base
- **Tool Execution**: Code generation, file operations, and command execution
- **Debugging Agent**: Error analysis and troubleshooting assistance
- **Speech-to-Text**: Whisper model integration for voice input
- **Validation Gate**: Response quality checking and refinement
- **Conversation History**: Maintains chat context across sessions
- **Modern Frontend**: React-based UI with dark mode support

## Architecture

```
final_fixed/
├── api/                 # FastAPI backend
│   └── main.py         # API endpoints and orchestration
├── core/               # Base classes and utilities
│   ├── base.py         # Agent base classes
│   ├── llm.py          # Ollama LLM interface
│   ├── config.py       # Configuration
│   ├── logger.py       # Logging setup
│   ├── memory.py       # Session memory
│   └── orchestrator.py # Intent classification and routing
├── agents/             # Specialized agents
│   ├── rag_agent.py    # RAG with ChromaDB
│   ├── tool_agent.py   # Tool execution
│   ├── debug_agent.py  # Debugging assistance
│   ├── llm_agent.py    # General conversational AI
│   ├── validation_agent.py # Response validation
│   └── speech_agent.py # Whisper STT
├── storage/            # Data persistence
│   ├── chat_storage.py # JSON-based chat storage
│   └── vector_storage.py # ChromaDB wrapper
├── frontend/           # React frontend
│   └── src/            # Frontend source code
├── data/               # Documents for RAG
├── chats/              # Chat sessions storage
├── chroma_db/          # Vector database
├── temp/               # Temporary files
└── requirements.txt    # Python dependencies
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- Ollama with Llama3.2 model installed

## Setup

### 1. Install Ollama and Llama3.2

```bash
# Install Ollama
# Visit: https://ollama.ai

# Pull Llama3.2 model
ollama pull llama3.2
```

### 2. Backend Setup

```bash
cd final_fixed

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# (Optional) Ingest documents into RAG knowledge base
python ingest_rag.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Backend Server

```bash
# From final_fixed directory
python api/main.py
```

The backend will run on `http://localhost:8000`

### 5. Configure Frontend

1. Open the frontend in your browser (default: `http://localhost:5173`)
2. Click the gear icon (top right)
3. Enter backend URL: `http://localhost:8000/chat`
4. Save

## Usage

### Chat Interface

- Type your question in the chat input
- Press Enter to send
- Use Shift+Enter for new lines
- Attach files/screenshots using the 📎 button
- Use voice input with the 🎙 button (if supported)

### Adding Documents to Knowledge Base

1. Place documents in the `data/` folder (supported: .txt, .md, .pdf, .docx)
2. Run the ingestion script:
```bash
python ingest_rag.py
```

### API Endpoints

- `POST /chat` - Process chat messages
- `GET /chats` - List all chat sessions
- `GET /chats/{chat_id}` - Get specific chat
- `DELETE /chats/{chat_id}` - Delete chat
- `PUT /chats/{chat_id}/title` - Update chat title

## Configuration

Edit `.env` file to configure:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
BACKEND_URL=http://localhost:8000
CHATS_DIR=chats
CHROMA_DIR=chroma_db
DATA_DIR=data
TEMP_DIR=temp
MAX_RETRIES=3
THRESHOLD=3.0
```

## Agent Routing

The orchestrator routes queries based on intent:

- **RAG Agent**: Questions about documentation/knowledge base
- **Tool Agent**: Code generation, file operations, commands
- **Debug Agent**: Error messages, troubleshooting
- **LLM Agent**: General conversation and greetings
- **Speech Agent**: Voice input transcription

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Verify Llama3.2 is installed: `ollama list`
- Check Ollama URL in `.env`

### No Documents in Knowledge Base
- Add documents to `data/` folder
- Run `python ingest_rag.py`
- Check ChromaDB directory exists

### Frontend Not Connecting
- Verify backend is running on port 8000
- Check CORS settings in `api/main.py`
- Ensure correct backend URL in frontend settings

### Conversation History Not Working
- Verify chat storage directory exists
- Check that messages are being saved to JSON files
- Ensure chat_id generation is working correctly

## Development

### Running Tests

```bash
# Run backend tests (if available)
pytest

# Run frontend tests
npm test
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist
```

## Project Structure

- **Backend**: FastAPI with SSE streaming support
- **Frontend**: React with TypeScript, TailwindCSS, shadcn/ui
- **Vector DB**: ChromaDB with sentence-transformers embeddings
- **LLM**: Ollama Llama3.2 (local, no API keys)
- **Speech**: OpenAI Whisper model

## License

This project is developed by Hazem Saker and Majd Nasser as part of a graduation-level project.

## Support

For issues or questions, please check the troubleshooting section or review the code documentation.
