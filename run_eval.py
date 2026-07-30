import os
import requests
import base64
import time
import glob

print("--- TESTING API ENDPOINTS ---")

# 1. Health check / Root UI endpoint
res = requests.get("http://localhost:8005/")
print(f"GET / : Status {res.status_code}, HTML Length: {len(res.text)}")
assert res.status_code == 200

# 2. Test Image Detection on all test images in tests/images
image_files = sorted(glob.glob("tests/images/*.jpg"))
print(f"\nFound {len(image_files)} test images in tests/images:")

success = 0
for img_path in image_files:
    fname = os.path.basename(img_path)
    with open(img_path, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")
    
    start = time.time()
    res = requests.post("http://localhost:8005/api/detect", json={"image_base64": b64})
    elapsed = (time.time() - start) * 1000
    
    data = res.json()
    faces = data.get("faces", [])
    print(f"  [{fname}] -> Status: {data.get('status')}, Faces: {len(faces)}, Time: {elapsed:.1f}ms")
    for face in faces:
        print(f"      Face at ({face['x']}, {face['y']}): Label='{face['label']}', Confidence={face['confidence']*100:.1f}%")
        if face['label'] != 'UNKNOWN':
            success += 1

print(f"\nDetection summary: {success} recognized face occurrences.")

# 3. Test Registration Endpoint
test_reg_path = image_files[0]
with open(test_reg_path, "rb") as f:
    b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

reg_res = requests.post("http://localhost:8005/api/register", json={"image_base64": b64, "name": "TEST_SUBJECT"})
print(f"\nPOST /api/register -> Status: {reg_res.status_code}, Response: {reg_res.json()}")

