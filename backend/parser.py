import os
from llm_ollama import ask_ollama
from prompts import base_prompt_template
import re
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


def parse_and_summarize(folder_path):
    summary_all = " # Code Documentation\n\n "

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()

                prompt = base_prompt_template.replace("<PASTE FILE CONTENT HERE>", code[:3000])
                summary = ask_ollama(prompt)
                summary = clean_response(summary)

                print(f"\n=== Summary for: {file_path} ===")
                print(summary)
                summary_all += f"\n## Summary for `{file}`\n\n{summary}\n"

    write_to_markdown(summary_all)
    print("\n Documentation generated at:", OUTPUT_DIR / "README.md")

# Run this
if __name__ == "__main__":
    parse_and_summarize("/Users/junaidshaikh/Documents/GItDocAI/sample_test/sample1")
