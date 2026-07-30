# 📁 NEXU | Subject Vector Seeding Dataset

> **Facial Identity Ingestion Directory**

---

## 📌 Usage Instructions

This folder stores reference subject images used by the **Nexu Cognitive Core** to seed facial identities during system startup.

1. **File Format:** Place `.jpg` or `.png` images directly in this folder.
2. **Subject Labeling:** Name each image file with the exact identity label you want recognized (e.g., `Elon Musk.jpg`, `Bill Gates.jpg`).
3. **Image Quality Guidelines:**
   - Use clear, well-lit frontal face portraits.
   - High resolution (at least 300x300 pixels).
   - Single face per photo for best embedding extraction.

---

## ⚡ How It Works

Upon server startup (`python main.py`), the backend automatically iterates through this directory, extracts a 128-dimensional vector embedding for each subject via **DeepFace FaceNet**, and stores it in memory (`REGISTERED_FACES`).

```text
dataset/
├── Bill Gates.jpg       -> Vectorized on boot
├── Elon Musk.jpg        -> Vectorized on boot
├── Lionel Messi.jpg     -> Vectorized on boot
├── Taylor Swift.jpg     -> Vectorized on boot
└── char1.jpg - char5.jpg
```

*Dynamic subjects registered through the web interface during runtime are also saved to memory automatically!*
