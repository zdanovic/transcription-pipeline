import whisper
from pathlib import Path

class AudioTranscriber:
    def __init__(self, model_size: str = "base"):
        # Loading the model is heavy, do it once at startup.
        # TODO: In a microservices architecture, consider deploying this behind a Triton/vLLM server instead.
        self.model = whisper.load_model(model_size)

    def process_file(self, file_path: Path) -> dict:
        # Whisper calls ffmpeg underneath to automatically downmix and resample to 16kHz
        # so we can skip explicit pydub/ffmpeg preprocessing for format standardization.
        result = self.model.transcribe(str(file_path))
        
        segments = [
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            }
            for segment in result["segments"]
        ]
        
        return {
            "transcription": result["text"].strip(),
            "segments": segments
        }

# Module-level instance to avoid reloading the model per request
transcriber = AudioTranscriber()
