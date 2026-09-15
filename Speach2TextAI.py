import sys
import base64
import json
import requests
import os

from pydub import AudioSegment
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

with open("config.json", "r") as f:
    CONFIG = json.load(f)


OPENROUTER_API_KEY = CONFIG.get("OPENROUTER_API_KEY")

# -----------------------------
# Background Thread
# -----------------------------
class TranscriptionThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, wav_path):
        super().__init__()
        self.wav_path = wav_path

    def run(self):
        try:
            # Convert WAV → MP3 (small file)
            mp3_path = "temp_audio.mp3"
            audio = AudioSegment.from_wav(self.wav_path)
            audio.export(mp3_path, format="mp3", bitrate="64k")

            # Read MP3 and base64 encode
            with open(mp3_path, "rb") as f:
                base64_audio = base64.b64encode(f.read()).decode("utf-8")

            # Send to Whisper
            response = requests.post(
                url="https://openrouter.ai/api/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "openai/whisper-1",
                    "input_audio": {
                        "data": base64_audio,
                        "format": "mp3"
                    }
                }),
                timeout=60
            )

            result = response.json()

            if "text" in result:
                self.finished.emit(result["text"])
            else:
                self.error.emit(json.dumps(result, indent=2))

            # Clean up
            if os.path.exists(mp3_path):
                os.remove(mp3_path)

        except Exception as e:
            self.error.emit(str(e))


# -----------------------------
# GUI
# -----------------------------
class VoiceToText(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WAV → MP3 → Text (Whisper via OpenRouter)")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        self.info = QLabel("Select a WAV file to transcribe.")
        layout.addWidget(self.info)

        self.textbox = QTextEdit()
        self.textbox.setPlaceholderText("Transcription will appear here...")
        layout.addWidget(self.textbox)

        btn = QPushButton("Open WAV File")
        btn.clicked.connect(self.open_file)
        layout.addWidget(btn)

        self.setLayout(layout)

        self.thread = None

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select WAV File",
            "",
            "WAV Files (*.wav)"
        )

        if not path:
            return

        self.info.setText(f"Processing: {path}")
        self.textbox.setPlainText("Converting WAV → MP3 and transcribing...")

        self.thread = TranscriptionThread(path)
        self.thread.finished.connect(self.show_result)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def show_result(self, text):
        self.textbox.setPlainText(text)
        self.info.setText("Done.")

    def show_error(self, err):
        self.textbox.setPlainText("Error:\n" + err)
        self.info.setText("Failed.")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceToText()
    window.show()
    sys.exit(app.exec())