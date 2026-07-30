import os
import base64
import time
import cv2
import requests

test_celebs = {
    "Scarlett_Johansson": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Scarlett_Johansson_in_2019_%28cropped%29.jpg",
    "Lionel_Messi": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Lionel_Messi_20180626_%28cropped%29.jpg",
    "Taylor_Swift": "https://upload.wikimedia.org/wikipedia/commons/3/33/Taylor_Swift_at_the_2024_Golden_Globes_%28cropped%29.jpg",
    "Elon_Musk": "https://upload.wikimedia.org/wikipedia/commons/9/99/Elon_Musk_Colorado_2022_%28cropped2%29.jpg"
}

print("\n--- INITIATING SYSTEM TESTS ---")
success_count = 0
total_count = 0

# Test 1: Uploading the Demo Images
print("\n[TEST: IMAGE UPLOADS]")
for name in test_celebs.keys():
    path = f"demo_assets/images/{name}.jpg"
    if not os.path.exists(path):
        print(f"File missing: {path}")
        continue
    total_count += 1
    with open(path, 'rb') as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode('utf-8')
    try:
        start = time.time()
        res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
        data = res.json()
        latency = time.time() - start
        
        expected_name = name.replace("_", " ")
        recognized = any(f["label"] == expected_name for f in data.get("faces", []))
        if recognized:
            print(f"✅ {expected_name}: RECOGNIZED ({latency:.2f}s latency)")
            success_count += 1
        else:
            labels = [f["label"] for f in data.get("faces", [])]
            print(f"❌ {expected_name}: FAILED (Detected: {labels})")
    except Exception as e:
        print(f"❌ {name}: API Error ({e})")

# Test 2: Uploading the Demo Videos (Simulating frontend video processing by sending a random frame)
print("\n[TEST: VIDEO UPLOADS (Frame Sampling)]")
for name in test_celebs.keys():
    path = f"demo_assets/videos/{name}.mp4"
    if not os.path.exists(path):
        print(f"File missing: {path}")
        continue
    total_count += 1
    
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 30) # Grab the 30th frame (1 second in)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"❌ {name}: Could not read video frame")
        continue
        
    _, buffer = cv2.imencode('.jpg', frame)
    b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
    
    try:
        start = time.time()
        res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
        data = res.json()
        latency = time.time() - start
        
        expected_name = name.replace("_", " ")
        recognized = any(f["label"] == expected_name for f in data.get("faces", []))
        if recognized:
            print(f"✅ {expected_name} (Video Frame): RECOGNIZED ({latency:.2f}s latency)")
            success_count += 1
        else:
            labels = [f["label"] for f in data.get("faces", [])]
            print(f"❌ {expected_name} (Video Frame): FAILED (Detected: {labels})")
    except Exception as e:
        print(f"❌ {name}: API Error ({e})")

print(f"\n--- TEST SUITE COMPLETE: {success_count}/{total_count} PASSED ---")
