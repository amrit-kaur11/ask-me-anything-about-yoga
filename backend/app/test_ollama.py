import requests

r = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "Say hello"
    }
)

print(r.text)