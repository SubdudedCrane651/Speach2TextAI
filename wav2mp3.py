import subprocess
import os
import sys


# ============================================================
# SETTINGS
# ============================================================

INPUT_WAV = "tts_output.wav"
OUTPUT_MP3 = "tts_output.mp3"

# Set to True if you want the WAV deleted after successful
# conversion.
DELETE_WAV_AFTER_CONVERSION = False

# MP3 quality
BITRATE = "128k"


# ============================================================
# CONVERT WAV TO MP3
# ============================================================

def convert_wav_to_mp3():

    print()
    print("========================================")
    print("       WAV → MP3 CONVERTER")
    print("========================================")
    print()

    # --------------------------------------------------------
    # Check WAV exists
    # --------------------------------------------------------

    if not os.path.isfile(INPUT_WAV):

        print("ERROR:")
        print(f"Cannot find: {INPUT_WAV}")
        print()
        print("Make sure the WAV file is in the same")
        print("folder as this Python program.")
        print()

        return False

    print(f"Input : {INPUT_WAV}")
    print(f"Output: {OUTPUT_MP3}")
    print()
    print("Converting...")
    print()

    # --------------------------------------------------------
    # Run FFmpeg
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                INPUT_WAV,
                "-codec:a",
                "libmp3lame",
                "-b:a",
                BITRATE,
                OUTPUT_MP3
            ],

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except FileNotFoundError:

        print()
        print("ERROR: FFmpeg was not found.")
        print()
        print("Install FFmpeg and make sure")
        print("ffmpeg.exe is available in your PATH.")
        print()

        return False

    # --------------------------------------------------------
    # Check FFmpeg result
    # --------------------------------------------------------

    if result.returncode != 0:

        print()
        print("ERROR: FFmpeg failed.")
        print()
        print(result.stderr)
        print()

        return False

    # --------------------------------------------------------
    # Verify MP3 was actually created
    # --------------------------------------------------------

    if not os.path.isfile(OUTPUT_MP3):

        print()
        print("ERROR:")
        print("FFmpeg reported an error because the MP3")
        print("file was not created.")
        print()

        return False

    # --------------------------------------------------------
    # Show file sizes
    # --------------------------------------------------------

    wav_size = os.path.getsize(INPUT_WAV)
    mp3_size = os.path.getsize(OUTPUT_MP3)

    print("========================================")
    print("          CONVERSION COMPLETE")
    print("========================================")
    print()
    print(f"Created: {OUTPUT_MP3}")
    print()
    print(f"WAV size: {wav_size / 1024 / 1024:.2f} MB")
    print(f"MP3 size: {mp3_size / 1024 / 1024:.2f} MB")
    print()

    # --------------------------------------------------------
    # Delete WAV if requested
    # --------------------------------------------------------

    if DELETE_WAV_AFTER_CONVERSION:

        try:

            os.remove(INPUT_WAV)

            print("Original WAV deleted.")

        except Exception as e:

            print(
                f"Warning: Could not delete WAV: {e}"
            )

    print()
    print("Done!")
    print()

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    success = convert_wav_to_mp3()

    if success:

        sys.exit(0)

    else:

        sys.exit(1)

