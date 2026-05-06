from pathlib import Path
import numpy as np
import time
import sounddevice as sd
from scipy.io.wavfile import write

def voice_input() -> Path:
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    audio_buffer = []
    sample_rate = 16000

    def callback(indata, frames, time, status):
        if status:
            print(f"Warning: {status}")
        audio_buffer.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        input("Recording... Press Enter to stop.")

    recording = np.concatenate(audio_buffer, axis=0).flatten()
    recording_int16 = (recording * 32767).astype(np.int16)

    timestamp = int(time.time())
    path = temp_dir / f"recording_{timestamp}.wav"

    write(str(path), sample_rate, recording_int16)

    return path
