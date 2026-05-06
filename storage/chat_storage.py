import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

class ChatStorage:
    """
    Storage system for chat history with multi-chat support.
    Uses JSON files for persistence.
    """
    
    def __init__(self, storage_dir: str = "chats"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def create_chat(self, title: str = None) -> str:
        """
        Create a new chat session.
        
        Args:
            title: Optional title for the chat
        
        Returns:
            Chat ID
        """
        chat_id = str(uuid.uuid4())
        chat_data = {
            "id": chat_id,
            "title": title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self._save_chat(chat_id, chat_data)
        return chat_id
    
    def get_chat(self, chat_id: str) -> Optional[Dict]:
        """
        Get a chat by ID.
        """
        chat_file = self.storage_dir / f"{chat_id}.json"
        if not chat_file.exists():
            return None
        
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_chats(self) -> List[Dict]:
        """
        List all chats with basic info.
        """
        chats = []
        for chat_file in self.storage_dir.glob("*.json"):
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                chats.append({
                    "id": chat_data["id"],
                    "title": chat_data["title"],
                    "created_at": chat_data["created_at"],
                    "updated_at": chat_data["updated_at"],
                    "message_count": len(chat_data["messages"])
                })
        
        # Sort by updated_at descending
        chats.sort(key=lambda x: x["updated_at"], reverse=True)
        return chats
    
    def add_message(self, chat_id: str, role: str, content: str) -> bool:
        """
        Add a message to a chat.
        
        Args:
            chat_id: Chat ID
            role: "user" or "assistant"
            content: Message content
        
        Returns:
            True if successful, False otherwise
        """
        chat_data = self.get_chat(chat_id)
        if not chat_data:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        chat_data["messages"].append(message)
        chat_data["updated_at"] = datetime.now().isoformat()
        
        self._save_chat(chat_id, chat_data)
        return True
    
    def get_messages(self, chat_id: str) -> List[Dict]:
        """
        Get all messages from a chat.
        """
        chat_data = self.get_chat(chat_id)
        if not chat_data:
            return []
        return chat_data["messages"]
    
    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat.
        """
        chat_file = self.storage_dir / f"{chat_id}.json"
        if chat_file.exists():
            chat_file.unlink()
            return True
        return False
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """
        Update chat title.
        """
        chat_data = self.get_chat(chat_id)
        if not chat_data:
            return False
        
        chat_data["title"] = title
        chat_data["updated_at"] = datetime.now().isoformat()
        
        self._save_chat(chat_id, chat_data)
        return True
    
    def _save_chat(self, chat_id: str, chat_data: Dict):
        """Helper to save chat data."""
        chat_file = self.storage_dir / f"{chat_id}.json"
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
