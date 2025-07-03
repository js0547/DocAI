base_prompt_template = """
You are an AI assistant generating clean GitHub README documentation.

Given the content of a Python file, generate:
1. A short **plain English** summary.
2. A bullet list of important functions or classes and what they do.
3. A sample usage block, if possible.

Format:
- No extra symbols like "**", "`", or headers like "###"
- Use clear titles like "Summary", "Functions", "Usage Example"
- Use plain markdown (hyphens, indentations, and new lines)

File content:
---------------------
<PASTE FILE CONTENT HERE>
"""
