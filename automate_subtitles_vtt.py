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
    vtt_file = os.path.join(video_dir, f"{base_name}.es.vtt")

    # Convert video to audio, but skip if audio file exists
    if os.path.exists(audio_file):
        print(f"Audio file {audio_file} already exists. Skipping audio conversion.")
    else:
        print(f"Converting {video_file} to audio...")
        run_command(f'ffmpeg -i "{video_file}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_file}"')

    # Run whisper.cpp to generate Spanish subtitles, but skip if vtt file exists
    if os.path.exists(vtt_file):
        print(f"Spanish subtitle file {vtt_file} already exists. Skipping subtitle generation.")
    else:
        print("Generating Spanish subtitles with whisper.cpp...")
        run_command(f'./build/bin/whisper-cli -m models/ggml-medium.bin -l es -ovtt -f "{audio_file}"', cwd="whisper.cpp")
        generated_vtt = f"{audio_file}.vtt"
        os.rename(generated_vtt, vtt_file)

    # Translate subtitles to each language
    for lang_code in LANGUAGE_CODES:
        output_vtt = os.path.join(video_dir, f"{base_name}.{lang_code}.vtt")
        if os.path.exists(output_vtt):
            print(f"Subtitle file {output_vtt} already exists. Skipping translation to {lang_code}.")
            continue
        print(f"Translating subtitles to {lang_code}...")
        if lang_code == "zh":
            command = f'./translate_vtt_google_translator.py "{vtt_file}" "{output_vtt}" {lang_code}'
        else:
            command = f'./translate_vtt.py "{vtt_file}" "{output_vtt}" llama3 {lang_code}'
        run_command(command)

    print("All subtitle translations completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./automate_subtitles_vtt.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    main(video_file)
