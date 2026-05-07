from pathlib import Path
from core.base import BaseAgent, AgentRequest, AgentResponse
from core.logger import logger
from core.config import Config


class SpeechAgent(BaseAgent):
    """Speech-to-text agent using Whisper."""
    
    def __init__(self):
        self.model_size = Config.WHISPER_SIZE
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            import whisper
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper model loaded: {self.model_size}")
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle speech transcription request."""
        file_path = request.metadata.get("file_path")
        
        if not file_path:
            return AgentResponse(
                status="error",
                message="No audio file path provided"
            )
        
        if not self.model:
            return AgentResponse(
                status="error",
                message="Whisper model not loaded"
            )
        
        try:
            result = self.transcribe(file_path)
            return AgentResponse(
                status="success",
                data={"text": result, "file_path": file_path},
                message=result
            )
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return AgentResponse(
                status="error",
                message=f"Transcription failed: {str(e)}"
            )
    
    def transcribe(self, file_path: str) -> str:
        """Transcribe audio file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        supported = [".wav", ".mp3", ".m4a", ".flac"]
        if path.suffix.lower() not in supported:
            raise ValueError(f"Unsupported format. Supported: {supported}")
        
        result = self.model.transcribe(str(file_path))
        return result.get("text", "").strip()
