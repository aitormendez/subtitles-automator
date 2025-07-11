#!/usr/bin/env python3
import subprocess
import sys
import os

LANGUAGE_CODES = ["en", "fr", "de", "it", "ru", "zh"]

def run_command(command, cwd=None):
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main(video_file):
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    video_dir = os.path.dirname(video_file)
    audio_file = os.path.join(video_dir, f"{base_name}.wav")
    srt_file = os.path.join(video_dir, f"{base_name}.es.srt")

    # Convert video to audio, but skip if audio file exists
    if os.path.exists(audio_file):
        print(f"Audio file {audio_file} already exists. Skipping audio conversion.")
    else:
        print(f"Converting {video_file} to audio...")
        run_command(f'ffmpeg -i "{video_file}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_file}"')

    # Run whisper.cpp to generate Spanish subtitles, but skip if srt file exists
    if os.path.exists(srt_file):
        print(f"Spanish subtitle file {srt_file} already exists. Skipping subtitle generation.")
    else:
        print("Generating Spanish subtitles with whisper.cpp...")
        run_command(f'./build/bin/whisper-cli -m models/ggml-medium.bin -l es -osrt -f "{audio_file}"', cwd="whisper.cpp")
        generated_srt = f"{audio_file}.srt"
        os.rename(generated_srt, srt_file)

    # Translate subtitles to each language
    for lang_code in LANGUAGE_CODES:
        output_srt = os.path.join(video_dir, f"{base_name}.{lang_code}.srt")
        print(f"Translating subtitles to {lang_code}...")
        if lang_code == "zh":
            command = f'./translate_srt_google_translator.py "{srt_file}" "{output_srt}" {lang_code}'
        else:
            command = f'./translate_srt.py "{srt_file}" "{output_srt}" llama3 {lang_code}'
        run_command(command)

    print("All subtitle translations completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./automate_subtitles_google_translator.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    main(video_file)
