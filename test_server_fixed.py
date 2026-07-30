import requests
import base64
import time
import os

img_path = 'dataset/Elon Musk.jpg'
if not os.path.exists(img_path):
    print("No image found for test.")
    exit(1)

with open(img_path, 'rb') as f:
    b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode('utf-8')

print("Testing detection...")
start = time.time()
res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
print("Detect Status:", res.status_code)
print("Detect Output:", res.json())
print("Time taken:", time.time() - start)
