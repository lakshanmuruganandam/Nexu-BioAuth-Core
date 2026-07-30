import requests
import json

payload = {
    "image_base64": "data:image/jpeg;base64," + "A" * 10_000_000,
    "name": "lakshan"
}

try:
    res = requests.post("http://localhost:8005/api/register", json=payload)
    print("Content-Type:", res.headers.get("content-type"))
    print("Status Code:", res.status_code)
    try:
        print("JSON:", res.json())
    except:
        print("Text:", res.text)
except Exception as e:
    print("Error:", e)
