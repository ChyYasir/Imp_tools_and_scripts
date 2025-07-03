import os
import platform
import yt_dlp
import whisper

def download_audio_and_get_title(youtube_url, output_dir="audio"):
    # Get video title safely
    ydl_opts_info = {
        'quiet': True,
        'skip_download': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        title = info_dict.get('title', 'audio').replace(" ", "_").replace("/", "_")

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


def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # Change to "small", "medium", or "large" if needed
    result = model.transcribe(audio_path)
    return result['text']


def save_transcription(title, transcription):
    # Sanitize filename
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    filename = f"transcription_{safe_title}.txt"

    # Write transcription to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(transcription)

    full_path = os.path.abspath(filename)
    print(f"✅ Transcription saved to: {full_path}")

    # Open file automatically
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


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=BJjsfNO5JTo"  # Replace with your own

    # Step 1: Download audio and extract title
    audio_path, title = download_audio_and_get_title(youtube_url)
    print(f"🎧 Audio downloaded: {audio_path}")

    # Step 2: Transcribe the audio
    transcription = transcribe_audio(audio_path)
    print(f"📝 First 1000 chars of transcription:\n{transcription[:1000]}")

    # Step 3: Save transcription to file
    save_transcription(title, transcription)
