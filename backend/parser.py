import os
import re
import argparse
from pathlib import Path
from llm_ollama import ask_ollama
from prompts import base_prompt_template

# Supported extensions
LANG_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".cpp": "C++"
}

# Default paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FOLDER = ROOT_DIR / "sample_test" / "sample1"
DEFAULT_OUTPUT = ROOT_DIR / "output_doc" / "sample1"

# Clean up LLM output
def clean_response(text):
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'`{1,3}', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# Write combined summary to markdown
def write_to_markdown(summary_text, filename="README.md", output_dir=DEFAULT_OUTPUT):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

# LLM summarization for list of files
def summarize_files(file_paths, outpath=DEFAULT_OUTPUT, outfile="README.md"):
    summary_all = "# 📘 Documentation\n\n"

    for file_path in file_paths:
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext not in LANG_MAP:
            print(f"❌ Skipping unsupported file: {file_path}")
            continue

        language = LANG_MAP[ext]
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            if not code.strip():
                print(f"⚠️ Skipping empty file: {file_path}")
                continue

            prompt = base_prompt_template.replace("<PASTE FILE CONTENT HERE>", code[:3000])
            summary = ask_ollama(prompt)
            summary = clean_response(summary)

            print(f"\n=== Summary for: {file_path} ({language}) ===")
            print(summary)
            summary_all += f"\n---\n\n### 📄 `{file_path.name}` ({language})\n\n{summary}\n"

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            summary_all += f"\n### 📄 `{file_path.name}` ({language})\n\n*Error: {e}*\n"

    write_to_markdown(summary_all, filename=outfile, output_dir=outpath)
    print(f"\n✅ Documentation saved to: {Path(outpath) / outfile}")

# Auto-find all files in a folder with optional filtering
def collect_files_from_folder(folder_path, filter_exts=None):
    collected_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = Path(file).suffix.lower()
            if filter_exts and ext not in filter_exts:
                continue
            if ext in LANG_MAP:
                collected_files.append(os.path.join(root, file))
    return collected_files

# === MAIN ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize code files using Ollama LLM")

    parser.add_argument("--file", type=str, help="A single file to summarize (relative or absolute)")
    parser.add_argument("--files", nargs="+", help="Multiple file paths to summarize")
    parser.add_argument("--ext", type=str, help="Comma-separated list of extensions (e.g. py,js)")
    parser.add_argument("--folder", type=str, help="Custom folder to scan instead of default")
    parser.add_argument("--outpath", type=str, help="Folder to save output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--outfile", type=str, help="Output filename", default="README.md")

    args = parser.parse_args()

    # Handle a single file
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            # Assume it's a relative file inside default folder
            file_path = DEFAULT_FOLDER / args.file
        summarize_files([file_path], outpath=args.outpath, outfile=args.outfile)

    # Handle multiple files
    elif args.files:
        resolved_files = []
        for f in args.files:
            file_path = Path(f)
            if not file_path.exists():
                file_path = DEFAULT_FOLDER / f
            resolved_files.append(file_path)
        summarize_files(resolved_files, outpath=args.outpath, outfile=args.outfile)

    # Handle folder scan mode
    else:
        ext_filters = {f".{ext.strip()}" for ext in args.ext.split(",")} if args.ext else None
        scan_folder = Path(args.folder) if args.folder else DEFAULT_FOLDER
        print(f"🔍 Scanning: {scan_folder}")
        file_list = collect_files_from_folder(scan_folder, ext_filters)
        summarize_files(file_list, outpath=args.outpath, outfile=args.outfile)
