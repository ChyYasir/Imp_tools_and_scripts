import os
import re
import platform
import yt_dlp
import whisper

# === Utility: Sanitize filename for Windows ===
def sanitize_filename(title):
    # Replace all illegal characters in filenames: \ / : * ? " < > | with _
    return re.sub(r'[\\/*?:"<>|]', "_", title).replace(" ", "_")


# === Step 1: Download Audio from YouTube ===
def download_audio_and_get_title(youtube_url, output_dir="audio"):
    # Get video title safely
    ydl_opts_info = {
        'quiet': True,
        'skip_download': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        title = sanitize_filename(info_dict.get('title', 'audio'))

    audio_output_path = f"{output_dir}_{title}"

    # Download best audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{audio_output_path}.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return f"{audio_output_path}.mp3", title


# === Step 2: Transcribe Audio Using Whisper ===
def transcribe_audio(audio_path, model):
    result = model.transcribe(audio_path)
    return result['text']


# === Step 3: Save Transcription to .txt and Open ===
def save_transcription(title, transcription):
    safe_title = sanitize_filename(title)
    filename = f"transcription_{safe_title}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(transcription)

    full_path = os.path.abspath(filename)
    print(f"\n✅ Transcription saved to: {full_path}")

    # Try to open the file automatically
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(filename)
        elif system == "Darwin":  # macOS
            os.system(f"open \"{filename}\"")
        else:  # Linux
            os.system(f"xdg-open \"{filename}\"")
    except Exception as e:
        print(f"⚠️ Could not open the file automatically: {e}")


# === Main Execution ===
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=u-3IILWQPRM"  # Replace with your own URL

    print("🔄 Downloading audio...")
    audio_path, title = download_audio_and_get_title(youtube_url)
    print(f"🎧 Audio downloaded: {audio_path}")

    print("🔄 Loading Whisper model...")
    model = whisper.load_model("small")  # You can use 'base', 'tiny', etc. for faster models
    print("✅ Model loaded.")

    print("📝 Transcribing audio...")
    transcription = transcribe_audio(audio_path, model)
    print(f"📋 Preview (first 1000 chars):\n{transcription[:1000]}")

    print("💾 Saving transcription...")
    save_transcription(title, transcription)
