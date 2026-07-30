import os
import cv2
import requests
import base64
import time

names = ["char1", "char2", "char3", "char4", "char5"]

print("\n--- INITIATING SYSTEM TESTS ---")
success_count = 0
total_count = 0

print("\n[TEST: IMAGE UPLOADS]")
for name in names:
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
        
        recognized = any(f["label"] == name for f in data.get("faces", []))
        if recognized:
            print(f"✅ {name}: RECOGNIZED ({latency:.2f}s latency)")
            success_count += 1
        else:
            labels = [f["label"] for f in data.get("faces", [])]
            print(f"❌ {name}: FAILED (Detected: {labels})")
    except Exception as e:
        print(f"❌ {name}: API Error ({e})")

print("\n[TEST: VIDEO UPLOADS]")
for name in names:
    path = f"demo_assets/videos/{name}.mp4"
    if not os.path.exists(path):
        print(f"File missing: {path}")
        continue
    total_count += 1
    
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 30)
    ret, frame = cap.read()
    cap.release()
    
    if not ret: continue
        
    _, buffer = cv2.imencode('.jpg', frame)
    b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
    
    try:
        start = time.time()
        res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
        data = res.json()
        latency = time.time() - start
        
        recognized = any(f["label"] == name for f in data.get("faces", []))
        if recognized:
            print(f"✅ {name} (Video Frame): RECOGNIZED ({latency:.2f}s latency)")
            success_count += 1
        else:
            labels = [f["label"] for f in data.get("faces", [])]
            print(f"❌ {name} (Video Frame): FAILED (Detected: {labels})")
    except Exception as e:
        print(f"❌ {name}: API Error ({e})")

print(f"\n--- TEST SUITE COMPLETE: {success_count}/{total_count} PASSED ---")
