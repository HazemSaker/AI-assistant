import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

def ask_llm(prompt: str, history: list = None) -> str:
    """
    Query Ollama Llama3.2 model with a prompt (non-streaming).
    
    Args:
        prompt: The prompt to send to the model
        history: Optional list of previous messages for context
    
    Returns:
        The model's response as a string
    """
    # Use chat API if history is provided
    if history and len(history) > 0:
        messages = []
        for msg in history:
            messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"
    else:
        # Simple generate API for single prompt
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"

def ask_llm_stream(prompt: str, history: list = None):
    """
    Query Ollama Llama3.2 model with streaming support.
    
    Args:
        prompt: The prompt to send to the model
        history: Optional list of previous messages for context
    
    Yields:
        Chunks of the response as they arrive
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }
    
    if history:
        payload["context"] = history
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to Ollama: {str(e)}"
