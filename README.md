<div align="center">
  <img src="https://img.shields.io/badge/Nexu-BioAuth_Core-0f172a?style=for-the-badge&logo=opencv" alt="NexuBioAuth Banner">
  <h1>Nexu BioAuth Core (NexuFace) ✦</h1>
  <p><b>Enterprise-Grade Facial Recognition & Authentication API</b></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)]()
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)]()
</div>

> **NexuBioAuth** is a secure, high-precision biometric authentication engine. Leveraging Dlib's deep learning models and OpenCV, it securely maps and stores 128-dimensional facial encodings, providing a scalable API for attendance systems, identity verification, and access control.

---

## 🏆 Biometric Security Without Compromise

Identity verification is currently dominated by expensive proprietary APIs that force companies to upload their users' sensitive biometric data to third-party clouds, violating GDPR and data sovereignty laws. NexuBioAuth runs entirely on-premise, ensuring complete zero-trust security.

### 🔥 Competitive Analysis: NexuBioAuth vs. The Industry

| Feature | NexuBioAuth (Ours) | AWS Rekognition | Azure Face API | Haar Cascades |
|---------|-----------------|-----------------|----------------|---------------|
| **Accuracy (LFW Benchmark)**| **99.38% (Dlib ResNet)** | 99%+ | 99%+ | < 80% (Highly Inaccurate) |
| **Data Sovereignty** | **100% On-Premise** | Stored on AWS | Stored on Azure | On-Premise |
| **Cost Per Verification**| **$0.00** | $0.001 | $0.001 | $0.00 |
| **Authentication Flow** | **Web API (Base64)** | SDK/API | SDK/API | Local Script Only |

As demonstrated, NexuBioAuth provides the state-of-the-art accuracy of a ResNet-34 Deep Metric Learning model (identical to AWS/Azure levels) but runs completely locally via Python and OpenCV, eliminating API latency and cloud costs.

---

## 🚀 Architecture & System Flow

```mermaid
graph TD
    A[Client WebRTC Camera] -->|POST Image Data| B(FastAPI Auth Gateway)
    B --> C{Image Normalization}
    C -->|HOG Face Detector| D[Bounding Box Extraction]
    D -->|ResNet-34 CNN| E[128D Embedding Generation]
    E --> F{Distance Metric (Tolerance 0.6)}
    F -->|Match Found| G[Generate Session Token]
    F -->|No Match| H[Auth Rejected 401]
    G --> I[JSON Success Payload]
    H --> I
    I --> A
```

### 1. 128-Dimensional Deep Metric Learning
Instead of comparing pixels, the system extracts a 128-measurement vector (embedding) that mathematically describes the face. To authenticate, we calculate the Euclidean distance between the login face vector and the database face vector. If the distance is `< 0.6`, identity is confirmed.

### 2. The Database Layer
The system uses `Pickle` and `Face_Recognition` arrays for high-speed local development, but the architecture allows for instantaneous mapping to a vector database like Pinecone or Milvus for enterprise-scale 1-to-N matching.

---

## ⚙️ Installation & Usage

### Prerequisites
- Python 3.10+
- CMake (for Dlib)
- OpenCV, Face_Recognition, FastAPI

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/lakshanmuruganandam/Nexu-BioAuth-Core.git
cd Nexu-BioAuth-Core

# 2. Install dependencies (Requires C++ build tools for Dlib)
pip install cmake fastapi uvicorn opencv-python face_recognition python-multipart

# 3. Boot the API Server
python main.py
```
*The VisionOS BioAuth Dashboard will be available at `http://localhost:8005/`.*

---

## 🤝 Contributing
We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---
<div align="center">
  <b>Security in Every Pixel. Built by Lakshan Muruganandam.</b>
</div>
