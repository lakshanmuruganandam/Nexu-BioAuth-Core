import cv2
import requests
import base64
import time
import glob
import os

video_files = sorted(glob.glob("tests/videos/*.mp4"))
print(f"Testing {len(video_files)} video files in tests/videos/:")

for vpath in video_files:
    fname = os.path.basename(vpath)
    cap = cv2.VideoCapture(vpath)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 15)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"  [{fname}] -> Could not read frame")
        continue
        
    _, buffer = cv2.imencode('.jpg', frame)
    b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
    
    start = time.time()
    res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
    latency = (time.time() - start) * 1000
    
    data = res.json()
    faces = data.get("faces", [])
    print(f"  [{fname}] -> Status: {data.get('status')}, Faces: {len(faces)}, Time: {latency:.1f}ms")
    for face in faces:
        print(f"      Label='{face['label']}', Confidence={face['confidence']*100:.1f}%")

