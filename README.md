# Teachable Machine Clone

## 🎯 Project Overview

**Teachable Machine Clone** is a **web‑based, no‑code image classifier** built with:
- **FastAPI** (backend) – thin controller layer that delegates all work to utility modules.
- **Streamlit** (frontend) – beautiful, responsive UI with premium styling (glass‑morphism, custom fonts, smooth animations).
- **MobileNetV3‑Large** (feature extractor) – frozen pretrained CNN that turns any image into a 960‑dimensional feature vector.
- **Support Vector Machine (RBF kernel)** – lightweight classifier that works well on tiny custom datasets (5‑30 images per class).

The app mirrors the spirit of Google’s *Teachable Machine* but runs **entirely locally**, requires **no Docker**, and is **fully extensible** for developers.

---

## ✨ Key Features

- **Zero‑code UI** – create, rename, and delete classes; upload images via file picker or webcam.
- **Live training** – extract MobileNetV3 features on‑the‑fly, train an SVM, and instantly see cross‑validation accuracy.
- **Confidence gating** – predictions below a 60 % threshold are marked *uncertain* to avoid misleading results.
- **Modular architecture** – thin FastAPI routes, separate `data_utils` (I/O) and `ml_utils` (ML) modules.
- **Premium UI** – glass‑morphism cards, custom Google Font **Outfit**, dynamic gradients, and micro‑animations.
- **Cross‑platform** – works on Windows, macOS, Linux (Python 3.11+).

---

## 📂 Repository Structure

```
teachable-machine-clone/
├── backend/                     # FastAPI server
│   ├── app/                     # Application package
│   │   ├── __init__.py          # Makes app a package (do not edit)
│   │   ├── main.py              # HTTP routes – thin controller only
│   │   ├── config.py            # Centralised settings (paths, thresholds)
│   │   └── utils/               # Helper modules
│   │       ├── __init__.py      # Package marker
│   │       ├── data_utils.py    # Filesystem ops (save, list, reset)
│   │       └── ml_utils.py      # Feature extraction, training, prediction
│   ├── dataset/                 # Auto‑created – one folder per class
│   ├── models/                  # Trained `model.pkl`
│   └── requirements.txt         # Backend dependencies
│
├── frontend/                    # Streamlit UI
│   ├── app.py                   # UI logic – only API calls, no ML
│   └── requirements.txt         # Frontend dependencies
│
├── README.md                    # **This file** – project documentation
└── .gitignore
```

---

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.11+** (recommended via `pyenv` or the official installer)
- **Git** (optional, for cloning)
- **Windows** (the current workspace) – the same steps work on macOS/Linux.

### 1️⃣ Clone the repository (if you haven’t already)
```bash
git clone https://github.com/your‑username/teachable-machine-clone.git
cd teachable-machine-clone
```

### 2️⃣ Backend – FastAPI
```bash
cd backend
# Create a virtual environment inside the project (keeps everything tidy)
python -m venv venv
# Activate – Windows PowerShell
./venv/Scripts/Activate.ps1   # or `venv\Scripts\activate` in cmd
# Install dependencies
pip install -r requirements.txt
# Run the server (auto‑reload enabled)
uvicorn app.main:app --reload --port 8000
```
Open **http://localhost:8000/docs** for the interactive Swagger UI.

### 3️⃣ Frontend – Streamlit
Open a *new* terminal (keep the backend running):
```bash
cd ../frontend
pip install -r requirements.txt
streamlit run app.py
```
The UI will be served at **http://localhost:8501**.

---

## 📚 How It Works – Architecture Deep Dive

### 1️⃣ Data Flow
1. **Upload** – images are sent via multipart `POST /upload-sample`. `data_utils.save_images` stores them under `backend/dataset/<class>/` with UUID filenames.
2. **Training** – `POST /train` triggers:
   - Scan all class folders.
   - For each image, `ml_utils.extract_features` runs the frozen MobileNetV3 to get a 960‑dim L2‑normalized vector.
   - Train an **RBF‑SVM** (`sklearn.svm.SVC`) with `class_weight='balanced'` and `probability=True`.
   - Optional **Stratified K‑Fold** cross‑validation (≥5 images per class) → returns `cv_accuracy`.
   - Save `model.pkl` containing the SVM, `LabelEncoder`, and class list.
3. **Prediction** – `POST /predict` loads the saved model, extracts features for the supplied image, obtains class probabilities, and applies the **confidence gate** (default 60 %).

### 2️⃣ Code Separation
- **`main.py`** – only declares the 6 endpoints (`/`, `/classes`, `/upload-sample`, `/train`, `/predict`, `/reset`). No file I/O or ML logic here.
- **`data_utils.py`** – pure filesystem utilities: sanitize class names, validate images, count samples, reset dataset.
- **`ml_utils.py`** – all heavy lifting:
  - `build_extractor()` – loads MobileNetV3 once at import time (global `EXTRACTOR`).
  - `extract_features(img)` – runs image through extractor, L2‑normalises.
  - `train_model()` – orchestrates dataset scan, feature extraction, SVM training, cross‑validation, and model persistence.
  - `predict_image(bytes)` – predicts a single image.
- **`config.py`** – single source of truth for paths, image size, ImageNet means/std, confidence threshold, and SVM hyper‑parameters (C, gamma).

---

## 🔌 API Reference
| Method | Path | Description | Returns |
|--------|------|-------------|---------|
| `GET` | `/` | Health check – returns `{"status": "ok"}` | 200 |
| `GET` | `/classes` | Lists class names and image counts | `{ "classes": ["Cat","Dog"], "counts": {"Cat": 12, "Dog": 9} }` |
| `POST` | `/upload-sample` | `class_name` (form) + `files[]` (multipart). Saves images to `dataset/<class>/`. | `{ "detail": "saved X images" }` |
| `POST` | `/train` | Triggers full training pipeline. | See `train_model()` output (classes, sample counts, `cv_accuracy` optional). |
| `POST` | `/predict` | `file` (multipart). Returns prediction dict: `{ "predicted_class": "Cat", "confidence": 91.3, "uncertain": false, "all_probabilities": {"Cat": 91.3, "Dog": 8.7}, "message": "Predicted 'Cat'..." }` |
| `DELETE` | `/reset` | Deletes *all* images in `dataset/` and removes `model.pkl`. | `{ "detail": "reset complete" }` |

---

## 🎨 Frontend UI Walkthrough
1. **Sidebar – System Control**
   - Shows backend connection status (green/red banner).
   - *Reset Everything* button wipes dataset & model.
2. **Column 1 – Classes Dashboard**
   - Edit class names (renames backend folder).
   - Delete a class (removes folder).
   - Upload files **or** capture via webcam per class.
   - Dynamic count badge (green ≥ 5, yellow < 5).
   - *Add a class* button creates a placeholder (e.g., `Class 3`).
3. **Column 2 – Training Card**
   - Shows readiness – requires ≥ 2 classes each with ≥ 5 images.
   - *Train Model* button (disabled until ready).
   - After training, display total images, optional cross‑val accuracy, and an expandable *Advanced Settings* panel (explains MobileNetV3, SVM hyper‑params, confidence gate).
4. **Column 3 – Preview & Test**
   - If untrained, a locked placeholder is shown.
   - When trained, choose **Upload** or **Webcam** to test.
   - Results display image, prediction badge (blue for confident, amber for uncertain), confidence percentages, and per‑class progress bars.
5. **Footer** – credits the feature extractor and classifier.

---

## 🛠️ Configuration (`backend/app/config.py`)
```python
from pathlib import Path

class Settings:
    # Directories (relative to this file)
    DATASET_DIR = Path(__file__).parent.parent / "dataset"
    MODEL_DIR   = Path(__file__).parent.parent / "models"
    MODEL_PATH  = MODEL_DIR / "model.pkl"

    # ImageNet stats used by MobileNetV3 normalisation
    IMAGENET_MEAN = (0.485, 0.456, 0.406)
    IMAGENET_STD  = (0.229, 0.224, 0.225)

    # Accepted file extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    # Confidence gate (float in [0,1]) – predictions below are marked "uncertain"
    CONFIDENCE_THRESHOLD = 0.60

    # SVM hyper‑parameters – feel free to tune
    SVM_C = 10.0
    SVM_GAMMA = "scale"

settings = Settings()
```
Edit any of these values to change paths, thresholds, or SVM regularisation.

---

## 🧪 Testing & Debugging
- **Unit tests** – not bundled but can be added with `pytest`. Focus on `data_utils` (folder creation, image validation) and `ml_utils` (feature extraction shape, model persistence).
- **Common errors** (see README table):
  | Symptom | Fix |
  |---|---|
  | `Backend offline` in sidebar | `cd backend && uvicorn app.main:app --reload` |
  | `Need at least 2 classes` | Create a second class and upload ≥ 5 images each |
  | `Uncertain prediction` | Add more diverse images or increase sample count |
  | `CV accuracy < 75 %` | Classes may be visually too similar – add a `None/Other` class |

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/awesome‑feature`).
3. Install the *development* dependencies (same as production plus `pytest`, `black`, `isort`).
4. Write tests and ensure `pytest` passes.
5. Submit a PR with a clear description of the change.

> **Style guidelines** – Follow Black formatting (`black .`), use type hints, and keep the thin‑controller / fat‑service separation intact.

---

## 📜 License
MIT License – feel free to use, modify, and distribute.

---

## 🙏 Acknowledgements
- **MobileNetV3** – pretrained on ImageNet, provided by `torchvision`.
- **scikit‑learn** – SVM implementation and utilities.
- **Streamlit** – the low‑code UI framework that makes rapid prototyping a breeze.
- **FastAPI** – lightning‑fast async API server.
- **Google Fonts – Outfit** – modern typography used throughout the UI.

---

## 📞 Support & Contact
For bugs, feature requests, or questions, open an issue on GitHub or contact the author at `rafaymuhammad901@gmail.com`.

---

*Happy teaching!*
