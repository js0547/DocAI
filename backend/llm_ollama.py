# llm_ollama.py
import requests

def ask_ollama(prompt):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"]
