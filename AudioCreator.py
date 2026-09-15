from gtts import gTTS
from pydub import AudioSegment

text = "This is just a test, it's amazing what can be done with AI."
tts = gTTS(text)
tts.save("test.mp3")

AudioSegment.from_mp3("test.mp3").export("test.wav", format="wav")
