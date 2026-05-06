from pathlib import Path
from dataclasses import dataclass, field
import whisper
import os

@dataclass(frozen=True)
class TranscriptionResult:
    file_name: str
    text: str
    metadata: dict = field(default_factory=dict)

class WhisperSTT:
    def __init__(self, model_size = "base", device = "cuda"):
        self.model = whisper.load_model(model_size, device=device)
        

    # Validate audio file
    def validate_audio_file(self, file_path: str):
        path = Path(file_path)
        supported_formats = [".wav", ".mp3", ".m4a", ".flac"]
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if path.suffix.lower() not in supported_formats:
            raise ValueError(f"Unsupported format {path.suffix}. Supported: {supported_formats}")

    # Transcribe audio using Whisper
    def transcribe_audio(self, file_path: str) -> TranscriptionResult:
        self.validate_audio_file(file_path)
        result = self.model.transcribe(str(file_path))
        return TranscriptionResult(
            file_name=os.path.basename(file_path),
            text=result.get("text", "").strip(),
            metadata={
                "language": result.get("language"),
                "segments_count": len(result.get("segments", [])),
                "device": str(next(self.model.parameters()).device)
            }
        )