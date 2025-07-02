# prompts.py
base_prompt_template = """
You are an AI developer assistant.

You are given the content of a Python file. Your job is to generate documentation for this file.

Please include:
1. A one-paragraph high-level summary.
2. A bullet list of important functions or classes with brief explanations.
3. If a main function or entry point exists, describe how to run the program.

File content:
----------------------
<PASTE FILE CONTENT HERE>
"""
