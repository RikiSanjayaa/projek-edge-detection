# Proyek Klasifikasi Koin Indonesia dengan Edge Detection + Hybrid Features

Proyek ini mengklasifikasikan koin Indonesia menggunakan **Hybrid Feature Extraction** (Original + Cropped) dengan Edge Detection, Hough Circle Transform, dan Machine Learning.

## Best Model Performance

**Random Forest + Fitur Hybrid**: **Akurasi 88.22%**

| Model                      | Accuracy   | Features | Method             |
| -------------------------- | ---------- | -------- | ------------------ |
| **Random Forest + Hybrid** | **88.22%** | 70       | Original + Cropped |
| Random Forest + Sobel      | 84.57%     | 35       | Original only      |
| SVM + Sobel                | 80.40%     | 35       | Original only      |

## Daftar Isi

- [Dataset](#dataset)
- [Panduan Instalasi](#panduan-instalasi)
- [Cara Cepat](#cara-cepat-menguji-model)
- [Struktur Proyek](#struktur-proyek)
- [Metodologi](#klasifikasi-koin-alur--metodologi)
- [Hasil](#hasil--artifak)
- [Teknologi](#teknologi-yang-digunakan)

## Dataset

**Klasifikasi Koin Indonesia** dari Kaggle:

- **4 kelas**: Koin Rp 100, Rp 200, Rp 500, Rp 1000
- **Total**: ~764 gambar (161 + 219 + 173 + 211)
- **Kondisi**: Berbagai sudut, pencahayaan, dan background (lantai, tangan)
- **Balanced**: Limit 150 gambar per kelas untuk menghindari ketidakseimbangan data
- **Image Size**: 512×512 pixels (4x resolusi dari baseline)

## Panduan Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/RikiSanjayaa/projek-edge-detection.git
cd projek-edge-detection
```

### 2. Create Virtual Environment

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Dataset from Kaggle

1. Unduh dataset dari: [Klasifikasi Koin](https://www.kaggle.com/datasets/ameeeliaas/klasifikasi-koin)
2. Ekstrak `archive.zip` ke folder `dataset/`
3. Struktur akhir harus seperti ini:
   ```
   dataset/
   ├── Koin Rp 100/
   ├── Koin Rp 200/
   ├── Koin Rp 500/
   └── Koin Rp 1000/
   ```

### 5. Verifikasi Instalasi

Periksa apakah dataset sudah diekstrak dengan benar:

```bash
ls dataset/
# Seharusnya menampilkan: Koin Rp 100  Koin Rp 1000  Koin Rp 200  Koin Rp 500
```

### 6. Jalankan Jupyter Notebook

```bash
jupyter notebook notebooks/coin-classification.ipynb
```

Jalankan semua sel secara berurutan untuk:

- Melatih model
- Membuat hasil evaluasi
- Membuat visualisasi
- Menyimpan model terlatih

## Struktur Proyek

```
projek-edge-detection/
├── .gitignore                        # File pengaturan git
├── README.md                         # Dokumentasi proyek
├── requirements.txt                  # Dependensi Python
├── preprocessing.py                  # Fungsi preprocessing (deteksi tepi, pemotongan)
├── test_model.py                     # Alat CLI untuk menguji model terlatih
├── dataset/                          # Dataset koin (unduh secara terpisah)
│   ├── Koin Rp 100/                 # 161 gambar
│   ├── Koin Rp 200/                 # 173 gambar
│   ├── Koin Rp 500/                 # 211 gambar
│   └── Koin Rp 1000/                # 219 gambar
├── notebooks/                        # Notebook Jupyter
│   ├── coin-classification.ipynb     # Utama: Klasifikasi koin (70 fitur hybrid)
│   ├── coin-classification2.ipynb    # Eksperimen: Fitur cropped saja (35 fitur)
│   ├── COIN-README.md               # Dokumentasi detail klasifikasi koin
│   └── experiment-fruit-identification.ipynb  # Legacy: Projek awal dari deteksi tepi ini
├── models/                           # Model terlatih (dibuat setelah training)
│   ├── random_forest_hybrid_model.pkl
│   └── random_forest_hybrid_scaler.pkl
└── results/                          # Hasil eksperimen (dibuat setelah training)
    ├── coin_classification/          # Hasil klasifikasi koin
    │   ├── confusion_matrix/
    │   ├── visualizations/
    │   ├── model_comparison.csv
    │   └── per_class_performance.csv
    └── coin_classification2/         # Hasil eksperimen cropped saja
```

**Catatan**: Folder `dataset/`, `models/`, dan `results/` tidak termasuk dalam repositori. Folder ini akan dibuat ketika Anda:

- Mengunduh dan mengekstrak dataset (langkah 4)
- Menjalankan notebook training (menghasilkan model dan hasil)

## Cara Cepat: Menguji Model

### Prasyarat

Sebelum menguji, Anda perlu:

1. Menyelesaikan langkah instalasi 1-4 (unduh repo, pasang dependensi, unduh dataset)
2. Melatih model dengan menjalankan `notebooks/coin-classification.ipynb` (menghasilkan file model)

### Uji Model Terlatih

Model menggunakan **Fitur Hybrid** (Original + Cropped) untuk akurasi terbaik.

```bash
# Uji dengan gambar koin
python test_model.py "dataset/Koin Rp 500/IMG_E2971.JPG"

# Dengan visualisasi (menyimpan langkah preprocessing)
python test_model.py "dataset/Koin Rp 500/IMG_E2971.JPG" --save-steps

# Ekspor ke JSON
python test_model.py "dataset/Koin Rp 500/IMG_E2971.JPG" --output result.json
```

**Contoh Output:**

```
======================================================================
COIN CLASSIFICATION - PREDICTION
======================================================================

Image: IMG_E2971.JPG
Model: Random Forest + Hybrid (Original + Cropped)
Size: (512, 512)

[OK] Coin detected: center=(256,256), radius=180px
Features extracted: 70 hybrid features (35 original + 35 cropped)

======================================================================
PREDICTION RESULT
======================================================================

Predicted: Koin Rp 500
Confidence: 93.21%
```

## Klasifikasi Koin: Alur & Metodologi

### Ekstraksi Fitur Hybrid

**Konsep**: Ekstrak fitur dari **2 versi** gambar yang sama:

1. **Segmentasi Original** (35 fitur):

   - Mempertahankan informasi ukuran absolut
   - Koin besar (Rp 1000) vs koin kecil (Rp 100) terbedakan
   - Fitur: radius, posisi, kepadatan tepi dalam skala original

2. **Dipotong & Diubah Ukuran** (35 fitur):
   - Potong sesuai diameter lingkaran, ubah ukuran ke 512×512
   - Menormalkan tekstur/pola (semua koin skala sama)
   - Fokus pada properti intrinsik koin, bukan ukuran

**Total**: **70 fitur** (35 original + 35 dipotong) = **Yang terbaik dari kedua metode!**

### Konfigurasi Optimal:

- **Ukuran Gambar**: 512×512 piksel (4x dari baseline 128×128)
- **Penyeimbangan Dataset**: 150 gambar per kelas
- **Filter Deteksi Lingkaran**: Hanya memproses gambar dengan lingkaran terdeteksi
- **Augmentasi Data**: 8x (rotasi, balik, kecerahan)

### Alur Preprocessing (Hybrid):

```
Gambar Input (512×512)
    ↓
Deteksi Tepi Sobel
    ↓
Hough Circle Transform
    ↓
┌─────────────────────────────┬──────────────────────────┐
│ Path 1: Original            │ Path 2: Cropped          │
│ Circular Segmentation       │ Crop to circle diameter  │
│ (preserves size info)       │ Resize to 512×512        │
│ Extract 35 features         │ Extract 35 features      │
└─────────────────────────────┴──────────────────────────┘
    ↓                               ↓
    └───────────── Concatenate ─────────────┘
                    ↓
            70 Hybrid Features
                    ↓
         StandardScaler Normalization
                    ↓
      Random Forest Classifier (200 trees)
                    ↓
              Prediction
```

### Ekstraksi Fitur (35 fitur per jalur, 70 total):

**Per Jalur (Original & Dipotong):**

- **Tekstur**: Kepadatan tepi, rata-rata, std, maks, histogram (12 fitur)
- **Bentuk**: Radius ternormalisasi, pusat x/y, kebulatan (4 fitur)
- **Pola Tepi**: Histogram orientasi, statistik gradien (12 fitur)
- **Spasial**: Kepadatan tepi per kuadran (4 fitur)
- **Tekstur Lokal**: Pengukuran berbasis variansi (3 fitur)

### Augmentasi Data (8x per gambar):

- **Rotasi**: 90°, 180°, 270°
- **Balik**: horizontal dan vertikal
- **Kecerahan**: penyesuaian (+/-)

### Model Machine Learning yang Dieksperimen:

**Fase 1: Model Baseline**

1. Random Forest + Canny (79.46%)
2. Random Forest + Sobel (84.57%)
3. SVM + Canny (73.62%)
4. SVM + Sobel (80.40%)

**Semua model** menggunakan **Ekstraksi Fitur Hybrid** (Original + Dipotong) untuk representasi fitur yang komprehensif.

### Eksperimen & Analisis:

Notebook `coin-classification.ipynb` melakukan:

1. Perbandingan visual Canny vs Sobel
2. Pelatihan 4 model dengan fitur hybrid
3. Ekstraksi fitur (70 fitur: 35 original + 35 dipotong)
4. Confusion matrix dan performa per kelas
5. Perbandingan model dan visualisasi

### Key Findings:

**Hybrid Approach:**

- Menggabungkan info ukuran (original) + konsistensi tekstur (dipotong)
- 70 fitur total (35 dari setiap versi)
- Fitur original mempertahankan diskriminasi skala absolut
- Fitur dipotong menormalkan pola tekstur

**Sobel vs Canny:**

- **Sobel menang** pada resolusi tinggi (512×512)
- Magnitudo gradien mempertahankan detail tekstur
- Lebih baik untuk pola koin dengan emboss

**Optimasi Dataset:**

- Penyeimbangan ke 150 gambar/kelas mengurangi bias
- Resolusi tinggi (512×512) penting untuk detail
- Filter deteksi lingkaran meningkatkan kualitas data

## Hasil & Artifak

### Model Tersimpan

- `models/random_forest_hybrid_model.pkl` (Model terbaik dengan fitur hybrid)
- `models/random_forest_hybrid_scaler.pkl`

### File Hasil

- `results/coin_classification/model_comparison_with_hybrid.csv`
- `results/coin_classification/per_class_performance.csv`
- `results/coin_classification/feature_importance_hybrid.png`
- `results/coin_classification/confusion_matrix/` - Semua confusion matrices
- `results/coin_classification/visualizations/` - Semua visualisasi

## Teknologi yang Digunakan

- **Python 3.10+**
- **OpenCV** - Pemrosesan gambar dan deteksi tepi
- **scikit-learn** - Klasifikasi machine learning (Random Forest, SVM)
- **NumPy** - Komputasi numerik
- **Pandas** - Manipulasi data
- **Matplotlib & Seaborn** - Visualisasi
- **Jupyter Notebook** - Interactive development
