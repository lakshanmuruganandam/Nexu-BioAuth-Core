import cv2
import base64
import numpy as np
import uvicorn
import time
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import warnings
from deepface import DeepFace

# Suppress warnings
warnings.filterwarnings("ignore")

app = FastAPI(title="Nexus Sentinel | True Facial Recognition AI")

# Load Haar Cascade for fast bounding boxes
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# In-memory database of registered faces
# Format: {"Subject Name": feature_vector_numpy_array}
REGISTERED_FACES = {}
SIMILARITY_THRESHOLD = 0.55

def load_dataset():
    if not os.path.exists("dataset"): return
    print("Loading datasets...")
    for f in os.listdir("dataset"):
        if f.endswith(".jpg") or f.endswith(".png"):
            name = f.rsplit(".", 1)[0]
            img_path = os.path.join("dataset", f)
            try:
                # Use DeepFace's default detector to find the face in the dataset image
                res = DeepFace.represent(img_path=img_path, model_name="Facenet", detector_backend="opencv", enforce_detection=False)
                if len(res) > 0:
                    REGISTERED_FACES[name] = np.array(res[0]["embedding"]).reshape(1, -1)
                    print(f"[Dataset] Registered: {name}")
            except Exception as e:
                print(f"[Dataset] Error loading {name}: {e}")

load_dataset()

class FrameRequest(BaseModel):
    image_base64: str

class RegisterRequest(BaseModel):
    image_base64: str
    name: str

def extract_face_feature(frame, x, y, w, h):
    """Crop the face and extract a feature vector using DeepFace Facenet."""
    # Add a slight margin
    margin = int(w * 0.1)
    y1, y2 = max(0, y-margin), min(frame.shape[0], y+h+margin)
    x1, x2 = max(0, x-margin), min(frame.shape[1], x+w+margin)
    
    face_crop = frame[y1:y2, x1:x2]
    if face_crop.size == 0:
        return None
        
    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    
    try:
        # Use DeepFace Facenet to extract state-of-the-art 128D embeddings
        # detector_backend="skip" because we already cropped the face using Haar Cascade
        res = DeepFace.represent(img_path=face_rgb, model_name="Facenet", detector_backend="skip", enforce_detection=False)
        return np.array(res[0]["embedding"]).reshape(1, -1)
    except Exception as e:
        return None

@app.post("/api/register")
async def register_face(req: RegisterRequest):
    try:
        img_data = base64.b64decode(req.image_base64.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return {"status": "error", "message": "No face detected in registration frame."}
            
        # Register the largest face found
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        x, y, w, h = faces[0]
        
        feature_vector = extract_face_feature(frame, x, y, w, h)
        if feature_vector is not None:
            REGISTERED_FACES[req.name.upper()] = feature_vector
            return {"status": "success", "message": f"Subject '{req.name}' successfully registered."}
        return {"status": "error", "message": "Failed to extract features."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/detect")
async def detect_faces(req: FrameRequest):
    try:
        img_data = base64.b64decode(req.image_base64.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        start_time = time.time()
        # Fast Haar Cascade detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        results = []
        for (x, y, w, h) in faces:
            # Extract deep learning features
            feature_vector = extract_face_feature(frame, x, y, w, h)
            
            label = "UNKNOWN"
            confidence = 0.0
            
            if feature_vector is not None and len(REGISTERED_FACES) > 0:
                # Compare against all registered faces using Cosine Similarity
                best_match_name = None
                best_match_score = -1
                
                for name, registered_vector in REGISTERED_FACES.items():
                    sim = cosine_similarity(feature_vector, registered_vector)[0][0]
                    if sim > best_match_score:
                        best_match_score = sim
                        best_match_name = name
                        
                if best_match_score > SIMILARITY_THRESHOLD:
                    label = best_match_name
                    confidence = float(best_match_score)
                else:
                    # Even if unknown, we still output the highest similarity score
                    confidence = float(best_match_score)
            
            results.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "label": label,
                "confidence": confidence
            })
            
        exec_ms = (time.time() - start_time) * 1000
            
        return {
            "faces": results, 
            "status": "success",
            "telemetry": {
                "algorithm": "FaceNet + Haar",
                "execution_ms": f"{exec_ms:.1f}ms",
                "faces_found": len(results),
                "db_size": len(REGISTERED_FACES)
            }
        }
    except Exception as e:
        return {"faces": [], "status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
