import sys
import requests
import json
import wave

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QComboBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal


# Load API key
with open("config.json", "r") as f:
    CONFIG = json.load(f)

OPENROUTER_API_KEY = CONFIG.get("OPENROUTER_API_KEY")


# -----------------------------
# Background Thread
# -----------------------------
class TTSThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text, voice):
        super().__init__()
        self.text = text
        self.voice = voice

    def run(self):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepgram/flux-tts:free",
                    "input": self.text,
                    "voice": self.voice
                },
                timeout=60
            )

            if response.status_code != 200:
                self.error.emit(response.text)
                return

            pcm_data = response.content  # RAW PCM 16-bit LE

            # -----------------------------
            # FIX: Wrap PCM in a WAV header
            # -----------------------------
            output_path = "tts_output.wav"

            sample_rate = 24000      # Flux-TTS default
            num_channels = 1         # Mono
            sample_width = 2         # 16-bit PCM

            with wave.open(output_path, "wb") as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)

            self.finished.emit(output_path)

        except Exception as e:
            self.error.emit(str(e))


# -----------------------------
# GUI
# -----------------------------
class TextToSpeechGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text → Speech (Flux-TTS Free)")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        self.info = QLabel("Enter text and choose a voice.")
        layout.addWidget(self.info)

        self.textbox = QTextEdit()
        self.textbox.setPlaceholderText("Type English text here...")
        layout.addWidget(self.textbox)

        # All supported Flux-TTS free voices
        voices = [
            "flux-alexis-en",
            "flux-bree-en",
            "flux-brittany-en",
            "flux-brooke-en",
            "flux-bruce-en",
            "flux-cliff-en",
            "flux-cole-en",
            "flux-colin-en",
            "flux-conor-en",
            "flux-donovan-en",
            "flux-drew-en",
            "flux-elise-en",
            "flux-gemma-en",
            "flux-haley-en",
            "flux-hannah-en",
            "flux-heather-en",
            "flux-jack-en",
            "flux-kai-en",
            "flux-kelsey-en",
            "flux-kit-en",
            "flux-maeve-en",
            "flux-marcelo-en",
            "flux-marcus-en",
            "flux-meena-en",
            "flux-meghan-en",
            "flux-miles-en",
            "flux-naveen-en",
            "flux-paige-en",
            "flux-priya-en",
            "flux-rufus-en",
            "flux-sean-en",
            "flux-sharon-en",
            "flux-sienna-en",
            "flux-tanner-en",
            "flux-wade-en",
            "flux-wes-en"
        ]

        self.voice_selector = QComboBox()
        self.voice_selector.addItems(voices)
        layout.addWidget(self.voice_selector)

        btn = QPushButton("Generate Speech")
        btn.clicked.connect(self.generate_speech)
        layout.addWidget(btn)

        self.setLayout(layout)

        self.thread = None

    def generate_speech(self):
        text = self.textbox.toPlainText().strip()
        if not text:
            self.info.setText("Please enter text first.")
            return

        voice = self.voice_selector.currentText()

        self.info.setText("Generating speech... please wait.")

        self.thread = TTSThread(text, voice)
        self.thread.finished.connect(self.show_result)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def show_result(self, path):
        self.info.setText(f"Speech generated: {path}")
        self.textbox.append(f"\nSaved as: {path}")

    def show_error(self, err):
        self.info.setText("Error occurred.")
        self.textbox.setPlainText("Error:\n" + err)


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextToSpeechGUI()
    window.show()
    sys.exit(app.exec())
