# ------------------------------------------------
# Save final WAV
# ------------------------------------------------

output_wav = "tts_output.wav"

self.progress.emit(
    "All parts generated. Combining audio..."
)

with wave.open(output_wav, "wb") as wav_file:

    wav_file.setnchannels(NUM_CHANNELS)
    wav_file.setsampwidth(SAMPLE_WIDTH)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(all_pcm_data)


# ------------------------------------------------
# Convert WAV to MP3
# ------------------------------------------------

output_mp3 = "tts_output.mp3"

self.progress.emit(
    "WAV created. Converting to MP3..."
)

try:

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            output_wav,
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "128k",
            output_mp3
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

except FileNotFoundError:

    raise RuntimeError(
        "FFmpeg was not found.\n\n"
        "Please install FFmpeg and make sure "
        "it is available in your Windows PATH."
    )

except subprocess.CalledProcessError as e:

    raise RuntimeError(
        "FFmpeg failed to convert the WAV to MP3.\n\n"
        + e.stderr
    )


# ------------------------------------------------
# Finished
# ------------------------------------------------

self.finished.emit(output_mp3)