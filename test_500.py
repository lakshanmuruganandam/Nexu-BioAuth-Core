import requests

try:
    res = requests.post("http://localhost:8005/api/register", json={"image_base64": "invalid", "name": "test"})
    print("Content-Type:", res.headers.get("content-type"))
    print("Status Code:", res.status_code)
    print("Text:", repr(res.text))
    print("JSON:", res.json())
except Exception as e:
    print("Error:", e)
