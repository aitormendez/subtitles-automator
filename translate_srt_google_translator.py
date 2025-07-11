#!/usr/bin/env python3
import sys
import re
import time
from googletrans import Translator

# Dictionary to map language codes to full details (name and google code)
LANGUAGE_DETAILS = {
    "en": {"name": "English", "google_code": "en"},
    "fr": {"name": "French", "google_code": "fr"},
    "de": {"name": "German", "google_code": "de"},
    "it": {"name": "Italian", "google_code": "it"},
    "ru": {"name": "Russian", "google_code": "ru"},
    "zh": {"name": "Simplified Chinese", "google_code": "zh-CN"},
}

def clean_translated_text(text, lang_code):
    """
    Cleans the translated text by removing unwanted patterns (e.g., surrounding quotes and notes).
    """
    # Remove potential surrounding quotes that some models might add
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    if text.startswith('“') and text.endswith('”'):
        text = text[1:-1]
    
    # Remove any remaining leading/trailing whitespace
    text = text.strip()
    
    if lang_code == "zh":
        # Remove parentheses notes (both ASCII and full-width Chinese)
        text = re.sub(r'[\(\（][^)\）]*[\)\）]', '', text)
        text = re.sub(r'\s{2,}', ' ', text).strip()
        
        # Remove lines starting with typical note markers or containing them
        lines = text.splitlines()
        filtered_lines = []
        for line in lines:
            if re.match(r'^\s*(Note|注意|请注意|译文|Translation)\s*[:：]', line, flags=re.IGNORECASE):
                continue  # Skip this line
            if any(marker in line for marker in ['Note:', 'Translation:', '请注意', '译文']):
                continue  # Skip lines with embedded notes
            filtered_lines.append(line)
        text = '\n'.join(filtered_lines).strip()
        
        # Remove trailing notes after quoted text
        text = re.sub(r'^(".*?")\s.*$', r'\1', text)
    
    return text

def translate_text_google(text, target_lang):
    """
    Translates text using Google Translate via googletrans library.
    """
    translator = Translator()
    try:
        result = translator.translate(text, dest=target_lang, src='es')
        return result.text
    except Exception as e:
        print(f"Google Translate error: {e}", file=sys.stderr)
        return None

def process_srt_file(input_file, output_file, lang_name, lang_code):
    """
    Reads an SRT file, translates the dialogue, and writes a new SRT file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}", file=sys.stderr)
        sys.exit(1)

    blocks = re.split(r'\n\s*\n', content.strip())
    total_blocks = len(blocks)
    print(f"Found {total_blocks} subtitle blocks to translate.")

    BATCH_SIZE = 5
    SEPARATOR = "⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻"

    with open(output_file, 'w', encoding='utf-8') as f_out:
        i = 0
        while i < total_blocks:
            batch = blocks[i:i + BATCH_SIZE]
            batch_texts = []
            batch_meta = []

            for block in batch:
                lines = block.split('\n')
                sequence_number = lines[0]
                timestamp = lines[1]
                original_text = "\n".join(lines[2:])
                batch_texts.append(original_text)
                batch_meta.append((sequence_number, timestamp))

            merged_text = SEPARATOR.join(batch_texts)
            target_lang = LANGUAGE_DETAILS[lang_code]["google_code"]
            translated_text = translate_text_google(merged_text, target_lang)

            if translated_text:
                translated_blocks = translated_text.split(SEPARATOR)
                for idx, (seq_num, timestamp) in enumerate(batch_meta):
                    if idx < len(translated_blocks):
                        cleaned_text = clean_translated_text(translated_blocks[idx], lang_code)
                        f_out.write(f"{seq_num}\n{timestamp}\n{cleaned_text}\n\n")
                        print(f"Block {i + idx + 1} translated successfully.")
            else:
                for idx, block in enumerate(batch):
                    f_out.write(f"{block}\n\n")
                    print(f"Failed to translate block {i + idx + 1}. Writing original text.", file=sys.stderr)

            i += BATCH_SIZE
            time.sleep(1)  # Pause to avoid overloading Google Translate

    print(f"\nTranslation complete. Output saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: ./translate_srt.py <input_file.srt> <output_file.srt> <lang_code>")
        print(f"Example: ./translate_srt.py tobias.webm.srt tobias.fr.srt fr")
        print("Supported language codes:", ", ".join(LANGUAGE_DETAILS.keys()))
        sys.exit(1)

    input_srt = sys.argv[1]
    output_srt = sys.argv[2]
    lang_code = sys.argv[3]

    if lang_code not in LANGUAGE_DETAILS:
        print(f"Error: Unsupported language code '{lang_code}'.")
        print("Supported codes are:", ", ".join(LANGUAGE_DETAILS.keys()))
        sys.exit(1)

    lang_name = LANGUAGE_DETAILS[lang_code]["name"]
    
    process_srt_file(input_srt, output_srt, lang_name, lang_code)
