import requests
from core.config import Config

class OllamaLLM:
    """Interface to Ollama LLM."""
    
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.base_url = Config.OLLAMA_URL

        self.url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"

    def generate(self, prompt: str, system: str = None, history: list = None) -> str:
        """Generate response from LLM with optional history."""
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
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            
            try:
                response = requests.post(self.chat_url, json=payload, timeout=60)
                response.raise_for_status()
                return response.json()["message"]["content"].strip()
            except Exception as e:
                return f"Error connecting to Ollama: {str(e)}"
        
        # Original generate logic for single prompt
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def chat(self, messages: list) -> str:
        """Chat with history support."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(self.chat_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
