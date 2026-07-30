import os
import subprocess
import base64
import time
import cv2
import json
import requests

# Setup directories
os.makedirs("dataset", exist_ok=True)
os.makedirs("demo_assets/images", exist_ok=True)
os.makedirs("demo_assets/videos", exist_ok=True)

# 1. Dataset Reference Images (To train the engine)
dataset_celebs = {
    "Scarlett_Johansson": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Scarlett_Johansson_by_Gage_Skidmore_2_%28cropped%29.jpg",
    "Lionel_Messi": "https://upload.wikimedia.org/wikipedia/commons/b/b4/Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg",
    "Taylor_Swift": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_%283%29.png"
}

# 2. Test Images (To verify recognition)
test_celebs = {
    "Scarlett_Johansson": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Scarlett_Johansson_in_2019_%28cropped%29.jpg",
    "Lionel_Messi": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Lionel_Messi_20180626_%28cropped%29.jpg",
    "Taylor_Swift": "https://upload.wikimedia.org/wikipedia/commons/3/33/Taylor_Swift_at_the_2024_Golden_Globes_%28cropped%29.jpg"
}

# Add Elon Musk and Bill Gates just to be safe as they are already downloaded
dataset_celebs["Elon_Musk"] = "https://upload.wikimedia.org/wikipedia/commons/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg"
test_celebs["Elon_Musk"] = "https://upload.wikimedia.org/wikipedia/commons/9/99/Elon_Musk_Colorado_2022_%28cropped2%29.jpg"

def download_image_curl(url, path):
    if not os.path.exists(path):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        cmd = f"curl -sL -A '{ua}' '{url}' -o '{path}'"
        res = subprocess.run(cmd, shell=True)
        if res.returncode != 0 or not os.path.exists(path) or os.path.getsize(path) < 1000:
            print(f"Failed to download {path}")
            return False
    return True

print("--- DOWNLOADING DATASETS & DEMO ASSETS ---")
for name, url in dataset_celebs.items():
    success = download_image_curl(url, f"dataset/{name.replace('_', ' ')}.jpg")
    if success: print(f"Dataset reference acquired: {name}")

for name, url in test_celebs.items():
    success = download_image_curl(url, f"demo_assets/images/{name}.jpg")
    if success: print(f"Test image acquired: {name}")

print("\n--- GENERATING SYNTHETIC DEMO VIDEOS ---")
# Create a 2-second panning video for each test image to simulate video uploads
def create_video_from_image(image_path, video_path):
    if os.path.exists(video_path) or not os.path.exists(image_path):
        return
    img = cv2.imread(image_path)
    if img is None: return
    
    # Resize image to a standard height for consistency
    h, w = img.shape[:2]
    target_h = 480
    scale = target_h / h
    img = cv2.resize(img, (int(w * scale), target_h))
    
    fps = 30
    duration = 2 # seconds
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (int(w * scale), target_h))
    
    # Simulate a subtle zoom-in effect for the video
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

for name in test_celebs.keys():
    create_video_from_image(f"demo_assets/images/{name}.jpg", f"demo_assets/videos/{name}.mp4")
    print(f"Demo video generated: {name}.mp4")


print("\n--- REBOOTING COGNITIVE CORE ---")
os.system("kill -9 $(lsof -t -i:8005) 2>/dev/null")
os.system("python main.py > core.log 2>&1 &")
time.sleep(15) # Wait for server and FaceNet to boot

print("\n--- INITIATING SYSTEM TESTS ---")
success_count = 0
total_count = 0

# Test 1: Uploading the Demo Images
print("\n[TEST: IMAGE UPLOADS]")
for name in test_celebs.keys():
    path = f"demo_assets/images/{name}.jpg"
    if not os.path.exists(path):
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
