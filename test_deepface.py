from deepface import DeepFace
import numpy as np
import time

start = time.time()
try:
    # Use dummy array instead of image
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    res = DeepFace.represent(img_path=dummy_img, model_name="Facenet", enforce_detection=False)
    print("Success. Embedding length:", len(res[0]["embedding"]))
except Exception as e:
    print("Error:", e)
print("Time:", time.time() - start)
