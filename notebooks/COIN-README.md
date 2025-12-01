# Klasifikasi Koin Rupiah: Edge Detection + CNN

## Overview

Proyek klasifikasi koin rupiah menggunakan:

- **Edge Detection**: Sobel (dengan CLAHE normalization)
- **Segmentasi**: Hough Circle Transform → Crop ke diameter
- **Dataset Split**: 8 kelas (4 nominal × 2 sisi: angka/gambar)
- **Model**: CNN, Random Forest, SVM

## Dataset

### Sumber Awal

- Kaggle: [Klasifikasi Koin](https://www.kaggle.com/datasets/ameeeliaas/klasifikasi-koin)
- 4 kelas asli: Rp 100, 200, 500, 1000

### Dataset Custom (8 Kelas)

Dataset di-split manual berdasarkan sisi koin:

```
dataset_splitted/
├── Koin Rp 100/
│   ├── angka/     # Sisi angka nominal
│   └── gambar/    # Sisi gambar/lambang
├── Koin Rp 200/
│   ├── angka/
│   └── gambar/
├── Koin Rp 500/
│   ├── angka/
│   └── gambar/
└── Koin Rp 1000/
    ├── angka/
    └── gambar/
```

**Download**: [Google Drive](https://drive.google.com/file/d/YOUR_FILE_ID_HERE/view?usp=sharing)

## Pipeline

```
Input Image
    ↓
Resize (256×256)
    ↓
CLAHE Normalization ← Menormalkan variasi pencahayaan
    ↓
Sobel Edge Detection
    ↓
Hough Circle Transform ← Deteksi lingkaran koin
    ↓
Crop to Circle Diameter ← Fokus pada area koin saja
    ↓
Resize (256×256)
    ↓
Edge Detection (Sobel)
    ↓
CNN / Random Forest / SVM
    ↓
Prediction (8 kelas)
```

### Kenapa Pakai Cropped Only?

- Menghilangkan background noise
- Normalisasi skala (semua koin ukuran sama)
- Fokus pada pattern koin, bukan ukuran absolut

### Kenapa Pakai CLAHE?

- Dataset punya variasi pencahayaan tinggi
- CLAHE = Contrast Limited Adaptive Histogram Equalization
- Membuat edge detection lebih konsisten

## Model yang Dicoba

### 1. CNN (Convolutional Neural Network)

- Input: 256×256×1 (grayscale edge image)
- 4 Conv blocks + 2 Dense layers
- 5 epochs, batch size 32
- **Akurasi: ~95%**

### 2. Random Forest + Feature Extraction

- 35 fitur manual (edge density, texture, shape, dll)
- 200 trees
- **Akurasi: ~85%**

### 3. SVM + Feature Extraction

- Kernel RBF
- **Akurasi: ~80%**

## Hasil

| Model         | Edge Method   | Akurasi  |
| ------------- | ------------- | -------- |
| **CNN**       | Sobel + CLAHE | **~95%** |
| Random Forest | Sobel         | ~85%     |
| SVM           | Sobel         | ~80%     |

### Kenapa CNN Lebih Bagus?

1. **Feature Learning**: CNN belajar fitur sendiri, tidak perlu manual extraction
2. **Spatial Hierarchy**: Menangkap pattern dari simple ke complex
3. **Translation Invariant**: Robust terhadap posisi pattern

## Data Augmentation

- Rotasi: 90°, 180°, 270°
- Flip: horizontal, vertical
- Brightness: +/- adjustment
- **Total**: 8x per gambar

## Files

### Notebooks

- `coin-classification-cnn.ipynb` - CNN 8 kelas (MAIN)
- `coin-classification.ipynb` - RF & SVM 4 kelas
- `coin-classification-splitted.ipynb` - RF & SVM 8 kelas

### Model Output

- `models/coin_classifier_cnn_8class.keras`
- `results/coin_classification_cnn/`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download dataset ke dataset_splitted/

# 3. Run notebook
jupyter notebook coin-classification-cnn.ipynb
```
