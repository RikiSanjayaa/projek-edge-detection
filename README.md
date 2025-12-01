# Klasifikasi Koin Rupiah dengan Edge Detection + CNN

Klasifikasi koin Indonesia (Rp 100, 200, 500, 1000) berdasarkan **nominal dan sisi koin** (angka/gambar) menggunakan Edge Detection dan CNN.

## Performa Model

| Model                 | Kelas   | Akurasi  |
| --------------------- | ------- | -------- |
| **CNN + Sobel Edge**  | 8 kelas | **~95%** |
| Random Forest + Sobel | 8 kelas | ~85%     |
| SVM + Sobel           | 8 kelas | ~80%     |

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
├── dataset/                      # download dari kaggle (https://www.kaggle.com/datasets/ameeeliaas/klasifikasi-koin)
├── dataset_splitted/             # Dataset 8 kelas (download terpisah)
├── notebooks/
│   ├── coin-classification-cnn.ipynb    # Utama: CNN 8 kelas
│   ├── coin-classification-splitted.ipynb    # ML Klasik Utama: (RF, SVM) 8 kelas
│   ├── coin-classification.ipynb        # ML klasik (RF, SVM) 4 kelas
│   └── COIN-README.md
├── models/
│   └── coin_classifier_cnn_8class.keras
└── results/
    └── coin_classification_cnn/
```

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

- Python 3.10+
- TensorFlow/Keras (CNN)
- OpenCV (Edge Detection, Hough Circle)
- scikit-learn (Random Forest, SVM)
- NumPy, Pandas, Matplotlib
