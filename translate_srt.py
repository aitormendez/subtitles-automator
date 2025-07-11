#!/usr/bin/env python3
import sys
import subprocess
import re
import time

# Dictionary to map language codes to full details (name and instruction for the model)
LANGUAGE_DETAILS = {
    "en": {"name": "English", "instruction": "Translate the following Spanish text to English. Provide ONLY the translated text."},
    "fr": {"name": "French", "instruction": "Translate the following Spanish text to French. Provide ONLY the translated text."},
    "de": {"name": "German", "instruction": "Translate the following Spanish text to German. Provide ONLY the translated text."},
    "it": {"name": "Italian", "instruction": "Translate the following Spanish text to Italian. Provide ONLY the translated text."},
    "ru": {"name": "Russian", "instruction": "Translate the following Spanish text to Russian. Provide ONLY the translated text."},
    "zh": {"name": "Simplified Chinese", "instruction": "Translate the following Spanish text to Simplified Chinese characters. Provide ONLY the translated text, using Hanzi characters. Do not include Pinyin, do not include phonetic guides, do not include extra comments, do not include explanations. Include just the translated Hanzi characters."},
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

def translate_text_ollama(text, model, lang_instruction_for_model, retries=3, delay=5):
    """
    Sends text to Ollama for translation and returns the translated text.
    Includes retry mechanism.
    """
    # The prompt is now more direct and emphasizes ONLY the translated text.
    prompt = f'''{lang_instruction_for_model} Text to translate: "{text}"'''
    
    command = [
        "ollama",
        "run",
        model,
        prompt
    ]
    
    for attempt in range(retries):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60) # Added timeout
            translated_text = result.stdout.strip()
            return translated_text
        except subprocess.CalledProcessError as e:
            print(f"Error running Ollama (Attempt {attempt + 1}/{retries}): {e}", file=sys.stderr)
            print(f"Stderr: {e.stderr}", file=sys.stderr)
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"Max retries reached for block. Giving up.", file=sys.stderr)
                return None
        except FileNotFoundError:
            print("Error: 'ollama' command not found. Make sure Ollama is installed and in your PATH.", file=sys.stderr)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print(f"Error: Ollama command timed out (Attempt {attempt + 1}/{retries}).", file=sys.stderr)
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"Max retries reached for block. Giving up.", file=sys.stderr)
                return None
        except Exception as e:
            print(f"An unexpected error occurred (Attempt {attempt + 1}/{retries}): {e}", file=sys.stderr)
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"Max retries reached for block. Giving up.", file=sys.stderr)
                return None

def process_srt_file(input_file, output_file, model, lang_name, lang_instruction_for_model, lang_code):
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

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for i, block in enumerate(blocks):
            if not block.strip():
                continue

            lines = block.split('\n')
            sequence_number = lines[0]
            timestamp = lines[1]
            original_text = "\n".join(lines[2:])

            print(f"Translating block {i + 1}/{total_blocks} to {lang_name}...")
            translated_text = translate_text_ollama(original_text, model, lang_instruction_for_model)

            if translated_text:
                # Clean the translated text before writing
                cleaned_text = clean_translated_text(translated_text, lang_code)
                f_out.write(f"{sequence_number}\n")
                f_out.write(f"{timestamp}\n")
                f_out.write(f"{cleaned_text}\n\n")
                print(cleaned_text) # Print the translated text to stdout
                print(f"Block {i + 1} translated successfully.")
            else:
                print(f"Failed to translate block {i + 1}. Writing original text.", file=sys.stderr)
                f_out.write(f"{block}\n\n") # Write original block if translation fails

    print(f"\nTranslation complete. Output saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./translate_srt.py <input_file.srt> <output_file.srt> <default_ollama_model> <lang_code>")
        print(f"Example: ./translate_srt.py tobias.webm.srt tobias.fr.srt llama3 fr")
        print("Supported language codes:", ", ".join(LANGUAGE_DETAILS.keys()))
        sys.exit(1)

    input_srt = sys.argv[1]
    output_srt = sys.argv[2]
    default_ollama_model = sys.argv[3] # This will be the default model
    lang_code = sys.argv[4]

    if lang_code not in LANGUAGE_DETAILS:
        print(f"Error: Unsupported language code '{lang_code}'.")
        print("Supported codes are:", ", ".join(LANGUAGE_DETAILS.keys()))
        sys.exit(1)

    # Determine which Ollama model to use based on language code
    ollama_model_to_use = default_ollama_model
    if lang_code == "zh":
       ollama_model_to_use = "qwen:7b-chat" # Use qwen for Chinese

    lang_name = LANGUAGE_DETAILS[lang_code]["name"]
    lang_instruction_for_model = LANGUAGE_DETAILS[lang_code]["instruction"]
    
    process_srt_file(input_srt, output_srt, ollama_model_to_use, lang_name, lang_instruction_for_model, lang_code)
