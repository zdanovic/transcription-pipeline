import whisper
from pathlib import Path

class AudioTranscriber:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)

    def process_file(self, file_path: Path) -> dict:
        result = self.model.transcribe(str(file_path))
        return {
            "transcription": result["text"].strip()
        }

transcriber = AudioTranscriber()
