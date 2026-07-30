import requests

# Intentionally send a malformed JSON or miss a required field
payload = {
    "image_base64": "data:image/jpeg;base64,12345"
    # Missing 'name'
}

try:
    res = requests.post("http://localhost:8005/api/register", json=payload)
    print("Status Code:", res.status_code)
    print("Response JSON:", res.json())
except Exception as e:
    print("Error:", e)
