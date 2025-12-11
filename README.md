# Klasifikasi Koin Rupiah dengan Edge Detection + CNN

Klasifikasi koin Indonesia (Rp 100, 200, 500, 1000) berdasarkan **nominal dan sisi koin** (angka/gambar) menggunakan Edge Detection dan CNN.

## Performa Model

| Model                               | Edge Detection | Akurasi    |
| ----------------------------------- | -------------- | ---------- |
| **Transfer Learning (ResNet18)**    | Tidak ada      | **98.15%** |
| **Transfer Learning (MobileNetV2)** | Tidak ada      | 83.73%     |
| **CNN Custom + Canny**              | Canny          | **96.86%** |
| CNN Custom + Sobel                  | Sobel          | 95.74%     |
| Random Forest + Sobel               | Sobel          | 81.02%     |
| Random Forest + Canny               | Canny          | 78.21%     |

### Temuan Penting

> **Preprocessing dengan edge detection (Canny) berhasil mencapai 96.86% - hanya selisih ~1.3% dari Transfer Learning (ResNet18) yang pre-trained pada 14 juta gambar ImageNet.**

Ini menunjukkan bahwa untuk domain spesifik seperti klasifikasi koin, **pemilihan preprocessing yang tepat** dapat mengkompensasi ketiadaan pre-trained knowledge.

## Dataset

**8 Kelas** (4 nominal × 2 sisi):

- Rp 100 Angka, Rp 100 Gambar
- Rp 200 Angka, Rp 200 Gambar
- Rp 500 Angka, Rp 500 Gambar
- Rp 1000 Angka, Rp 1000 Gambar

Dataset sudah di-split manual per sisi koin dan diproses dengan CLAHE + Edge Detection.

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/RikiSanjayaa/projek-edge-detection.git
cd projek-edge-detection
```

### 2. Buat Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Dataset (Custom - Sudah Diproses)

Dataset sudah di-split per sisi koin (angka/gambar).

**Download dari Google Drive:**

> [dataset_splitted.zip](https://drive.google.com/file/d/1QdmgXZseI1WfD_AfPKTjd1J5CBn3VFWL/view?usp=sharing)

Ekstrak ke root folder:

```
projek-edge-detection/
├── dataset_splitted/
│   ├── Koin Rp 100/
│   │   ├── angka/
│   │   └── gambar/
│   ├── Koin Rp 200/
│   │   ├── angka/
│   │   └── gambar/
│   ├── Koin Rp 500/
│   │   ├── angka/
│   │   └── gambar/
│   └── Koin Rp 1000/
│       ├── angka/
│       └── gambar/
```

### 5. Jalankan Notebook

```bash
jupyter notebook notebooks/coin-classification-cnn.ipynb
```

## Struktur Proyek

```
projek-edge-detection/
├── preprocessing.py              # Fungsi preprocessing (CLAHE, edge detection, crop)
├── test_model.py                 # CLI untuk testing model
├── requirements.txt
│
├── api/                          # FastAPI Backend
│   ├── main.py                   # API endpoints
│   ├── predictor.py              # Model loading & prediction
│   ├── .env.example              # Environment template
│   └── README.md                 # API documentation
│
├── web/                          # React Frontend
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   ├── .env.example              # Environment template
│   └── README.md                 # Web documentation
│
├── models/                       # Trained Models (not in git)
│   ├── coin_classifier_cnn_8class.keras
│   └── coin_classifier_8class_model.pkl
│
├── notebooks/                    # Jupyter Notebooks
│   ├── coin-classification-cnn-canny.ipynb  # CNN + Canny (96.86%)
│   ├── coin-classification-cnn.ipynb        # CNN + Sobel (95.74%)
│   ├── coin-classification-transfer-learning.ipynb  # Transfer Learning (98%)
│   └── coin-classification-splitted.ipynb   # Random Forest & SVM
│
├── dataset_splitted/             # Dataset (download separately)
└── results/                      # Training results
```

---

## Pipeline Preprocessing

```
Input Image
    ↓
Resize (256×256)
    ↓
CLAHE (Normalize lighting)
    ↓
Sobel Edge Detection
    ↓
Hough Circle Transform
    ↓
Crop to Circle Diameter
    ↓
Resize (256×256)
    ↓
CNN / ML Classifier
    ↓
Prediction (8 kelas)
```

## Teknologi

**Machine Learning:**

- TensorFlow/Keras (CNN Custom)
- PyTorch + torchvision (Transfer Learning: ResNet18, MobileNetV2)
- scikit-learn (Random Forest, SVM)
- OpenCV (Edge Detection: Canny & Sobel, Hough Circle Transform)

**Backend:**

- FastAPI
- Python 3.10+

**Frontend:**

- React 18
- Vite
- Tailwind CSS
- Lucide React

---

## Documentation

- [Docker Deployment](DOCKER.md) - Deploy dengan Docker
- [API Documentation](api/README.md)
- [Web Documentation](web/README.md)
- [Notebook Guide](notebooks/COIN-README.md)
