import os
import requests
import base64
import time

# 1. Download Dataset
os.makedirs("dataset", exist_ok=True)

# Direct Wikimedia URLs for reliability
celebs = {
    "Tom Cruise": "https://upload.wikimedia.org/wikipedia/commons/3/33/Tom_Cruise_by_Gage_Skidmore_2.jpg",
    "Keanu Reeves": "https://upload.wikimedia.org/wikipedia/commons/3/33/Reeves_at_the_2014_Toronto_International_Film_Festival.jpg"
}

print("Downloading dataset...")
headers = {"User-Agent": "Mozilla/5.0"}
for name, url in celebs.items():
    if os.path.exists(f"dataset/{name}.jpg"):
        print(f"Skipping {name}, already exists.")
        continue
        
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            with open(f"dataset/{name}.jpg", "wb") as f:
                f.write(res.content)
            print(f"Downloaded {name}")
        else:
            print(f"Failed to download {name}: {res.status_code}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")

time.sleep(1)

print("\nRestarting FastAPI Server to load new identities...")
os.system("kill -9 $(lsof -t -i:8005) 2>/dev/null")
os.system("python main.py &")
time.sleep(8) 

print("\nFetching a novel test image of Tom Cruise to test the engine...")
test_img_path = "test_image.jpg"
test_url = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Tom_Cruise_%2834450932580%29.jpg" # Different image of Tom Cruise
try:
    res = requests.get(test_url, headers=headers, timeout=10)
    if res.status_code == 200:
        with open(test_img_path, "wb") as f:
            f.write(res.content)
        print("Test image downloaded.")
except Exception as e:
    print(f"Failed to download test image: {e}")

if os.path.exists(test_img_path):
    print("\nRunning neural inference on test image...")
    with open(test_img_path, 'rb') as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode('utf-8')
    
    start = time.time()
    try:
        res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
        print(f"Status Code: {res.status_code}")
        data = res.json()
        print(f"Response: {data}")
        print(f"Time Taken: {time.time() - start:.2f}s")
        
        if data.get("faces") and data["faces"][0]["label"] == "Tom Cruise":
            print("\n✅ SUCCESS: Engine correctly identified Tom Cruise from a novel image!")
        else:
            print("\n❌ FAILURE: Could not confidently identify Tom Cruise.")
    except Exception as e:
        print(f"Error calling API: {e}")
else:
    print("No test image to process.")
