import os
from llm_ollama import ask_ollama
from prompts import base_prompt_template
import re
import argparse
from pathlib import Path


LANG_MAP ={
    ".py":"python",
    ".js":"JavaScript",
    ".java":"java",
    ".cpp":"C++"
}
# Get the root directory of the project dynamically
ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output_doc" / "sample1"

def clean_response(text):
    # Remove redundant asterisks, backticks
    text = re.sub(r'\*{1,3}', '', text)         # remove *, **, ***
    text = re.sub(r'`{1,3}', '', text)          # remove ` or ```
    text = re.sub(r'\n{3,}', '\n\n', text)      # compress too many newlines
    return text.strip()


def write_to_markdown(summary_text, filename="README.md", output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir/filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

def parse_and_summarize(folder_path, filter_exts=None): # Add filter_exts parameter
    summary_all = " # Code Documentation\n\n "

    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower() # Convert to lowercase for robust matching
            print(f"Found file: {file} (ext: {ext})") 
            
            # Apply the filter here
            if filter_exts and ext not in filter_exts:
                print(f"  Skipping file {file} due to extension filter.")
                continue # Skip to the next file if it doesn't match the filter

            if ext in LANG_MAP: # This check is still needed for overall language support
                 language = LANG_MAP[ext] 
                 print(f"--> Processing: {file} as {language}")  # DEBUG
                 file_path = os.path.join(root, file)
                 
                 with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()

                 if not code.strip():
                     print(f"  Skipping empty file: {file_path}")
                     continue

                 prompt = base_prompt_template.replace("<PASTE FILE CONTENT HERE>", code[:3000])
                 try:
                     summary = ask_ollama(prompt)
                     summary = clean_response(summary)
                     print(f"\n=== Summary for: {file_path} ({language}) ===")
                     print(summary)
                     summary_all += f"\n## Summary for `{file}`\n\n{summary}\n"
                 except Exception as e:
                     print(f"  Error processing {file_path} with Ollama: {e}")
                     summary_all += f"\n## Summary for `{file}`\n\n*Error generating summary: {e}*\n"
            else:
                # This else block will now only be hit if the file's extension
                # is not in LANG_MAP, after passing the filter (if any).
                print(f"  Skipping unsupported file: {file} (Extension: {ext})")


    write_to_markdown(summary_all)
    print("\n Documentation generated at:", OUTPUT_DIR / "README.md")
# Run this
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize code files using Ollama LLM")

    parser.add_argument(
        "--ext",
        type=str,
        help="Comma-separated list of file extensions to filter (e.g. js,py,java)",
        default=""
    )
    args=parser.parse_args()

    if args.ext:
        ext_filters = {f".{ext.strip()}"for ext in args.ext.split(",")}
    else:
        ext_filters= None
    
    parse_and_summarize(
        folder_path="/Users/junaidshaikh/Documents/GItDocAI/sample_test/sample1",
        filter_exts = ext_filters
    )