# System Test Scenarios

## Setup
1. Ensure Ollama is running: `ollama serve`
2. Start backend: `python main.py`
3. Start frontend: `cd frontend && bun run dev`
4. Open browser: `http://localhost:8080`

---

## Test Scenario 1: Basic Conversation (LLM Agent)
**Purpose:** Test basic LLM functionality

**Steps:**
1. Open the frontend
2. Type: "Hello, how are you?"
3. Send the message
4. Expected: Response from Llama3.2

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 2: Knowledge-Based Questions (RAG Agent)
**Purpose:** Test RAG with ChromaDB

**Setup:**
1. Add a test document to `data/python/` folder:
   ```python
   # Create file: data/python/basics.md
   # Python Basics
   Python is a high-level programming language.
   To print in Python, use: print("Hello World")
   Variables in Python don't need type declaration.
   ```

2. Run ingestion:
   ```bash
   python ingest_rag.py
   ```

3. Restart backend

**Test:**
1. Type: "How do I print in Python?"
2. Send the message
3. Expected: Response based on the ingested documentation

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 3: Code Generation (Tool Execution Agent)
**Purpose:** Test write_code tool

**Steps:**
1. Type: "Write a Python function to add two numbers"
2. Send the message
3. Expected: Code is written to temp/ and executed with output

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 4: File Operations (Tool Execution Agent)
**Purpose:** Test file read/write tools

**Steps:**
1. Type: "Create a file called test.txt with the content 'Hello World'"
2. Send the message
3. Expected: File created successfully

**Test:**
1. Type: "Read the contents of test.txt"
2. Send the message
3. Expected: Shows "Hello World"

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 5: Debugging (Debugging Agent)
**Purpose:** Test error analysis

**Steps:**
1. Type: "I'm getting this error: ImportError: No module named 'requests'. How do I fix it?"
2. Send the message
3. Expected: Detailed explanation of the error and solution

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 6: Multi-Turn Conversation
**Purpose:** Test conversation history

**Steps:**
1. Type: "What is Python?"
2. Send message
3. Type: "Can you give me an example?"
4. Send message
5. Expected: Response references previous context

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 7: Chat Management
**Purpose:** Test chat persistence and deletion

**Steps:**
1. Create a new chat
2. Send a message
3. Create another new chat
4. Send a different message
5. Switch back to first chat
6. Expected: Both chats preserved with their messages

**Test:**
1. Delete one chat
2. Expected: Chat removed from sidebar

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 8: RAG with Organized Data
**Purpose:** Test recursive folder ingestion

**Setup:**
1. Create folder structure:
   ```
   data/
   ├── javascript/
   │   └── js_basics.md
   ├── python/
   │   └── python_basics.md
   └── network/
       └── troubleshooting.md
   ```

2. Add content to each file

3. Run ingestion:
   ```bash
   python ingest_rag.py
   ```

**Test:**
1. Type: "How do I declare a variable in JavaScript?"
2. Send message
3. Expected: Response from JavaScript documentation

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 9: Empty Knowledge Base
**Purpose:** Test RAG behavior with no data

**Setup:**
1. Delete `chroma_db/` folder (if exists)
2. Restart backend

**Test:**
1. Type: "What is the meaning of life?"
2. Expected: Falls back to LLM agent (no RAG error)

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 10: Complex Query Routing
**Purpose:** Test agent routing logic

**Test Cases:**
- "Run a command to list files" → Tool agent
- "Debug this error: ..." → Debug agent  
- "What is X?" → RAG or LLM agent
- "Write code to Y" → Tool agent (write_code)

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 11: Error Handling
**Purpose:** Test system resilience

**Test Cases:**
1. Stop Ollama server
2. Try to send a message
3. Expected: Error message displayed

**Test:**
1. Restart Ollama
2. Send message again
3. Expected: System recovers

**Result:** ✅ Pass / ❌ Fail

---

## Test Scenario 12: Long Context
**Purpose:** Test with long conversation history

**Steps:**
1. Have a 10+ message conversation
2. Ask a question referencing earlier context
3. Expected: System maintains context correctly

**Result:** ✅ Pass / ❌ Fail

---

## Summary Checklist

- [ ] Scenario 1: Basic Conversation
- [ ] Scenario 2: RAG Knowledge Base
- [ ] Scenario 3: Code Generation
- [ ] Scenario 4: File Operations
- [ ] Scenario 5: Debugging
- [ ] Scenario 6: Multi-Turn Conversation
- [ ] Scenario 7: Chat Management
- [ ] Scenario 8: Organized Data Ingestion
- [ ] Scenario 9: Empty Knowledge Base
- [ ] Scenario 10: Query Routing
- [ ] Scenario 11: Error Handling
- [ ] Scenario 12: Long Context

---

## Notes
- Backend logs show which agent is handling each request
- Check `chats/` folder for backend chat storage
- Check `chroma_db/` for vector database
- Check `data/processed/` for ingested files
