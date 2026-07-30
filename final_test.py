import os
import glob
import shutil
import cv2
import requests
import base64
import time

brain_dir = "/Users/lakshanmuruganandam/.gemini/antigravity-cli/brain/8f9f339c-a9f1-4889-b3de-280e89149d59"

names = ["char1", "char2", "char3", "char4", "char5"]

for name in names:
    files = glob.glob(os.path.join(brain_dir, f"{name}_*.jpg"))
    if not files:
        print(f"File missing for {name}")
        continue
    img_path = files[-1] # Get latest
    
    # Save as training dataset
    shutil.copy(img_path, f"dataset/{name}.jpg")
    
    # Save as testing asset
    shutil.copy(img_path, f"demo_assets/images/{name}.jpg")
    
    # Create video asset
    img = cv2.imread(img_path)
    if img is not None:
        h, w = img.shape[:2]
        target_h = 480
        scale = target_h / h
        img = cv2.resize(img, (int(w * scale), target_h))
        
        fps = 30
        duration = 2
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f"demo_assets/videos/{name}.mp4", fourcc, fps, (int(w * scale), target_h))
        
        for i in range(fps * duration):
            zoom_factor = 1.0 + (i * 0.005)
            zh = int(target_h / zoom_factor)
            zw = int(img.shape[1] / zoom_factor)
            y = (target_h - zh) // 2
            x = (img.shape[1] - zw) // 2
            
            cropped = img[y:y+zh, x:x+zw]
            frame = cv2.resize(cropped, (img.shape[1], target_h))
            out.write(frame)
            
        out.release()
        print(f"Video created for {name}")

print("\n--- REBOOTING COGNITIVE CORE ---")
os.system("kill -9 $(lsof -t -i:8005) 2>/dev/null")
os.system("python main.py > core.log 2>&1 &")
time.sleep(15) # Wait for boot

print("\n--- INITIATING FINAL SYSTEM TESTS ---")
success_count = 0
total_count = 0

for name in names:
    path = f"demo_assets/images/{name}.jpg"
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
