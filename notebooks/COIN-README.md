# Projek Pengolahan Citra: Identifikasi Koin menggunakan Edge Detection + Hough Transform

## Daftar Isi

1. [Overview](#overview)
2. [Dataset](#dataset)
3. [Pipeline](#pipeline)
4. [Feature Engineering](#feature-engineering)
5. [Hasil Eksperimen](#hasil-eksperimen)
6. [Kesimpulan](#kesimpulan)
7. [Cara Menggunakan](#cara-menggunakan)

## Overview

Proyek ini mengklasifikasikan koin rupiah (Rp 100, Rp 200, Rp 500, Rp 1000) menggunakan:

- **Edge Detection**: Canny vs Sobel (untuk perbandingan)
- **Hough Circle Transform**: Deteksi lingkaran koin
- **Hybrid Feature Extraction**: Original + Cropped segmentation (70 features total)
- **Feature Extraction**: Texture, shape, edge pattern, dan spatial features
- **Machine Learning**: Random Forest vs SVM

## Dataset

- **Sumber**: Klasifikasi Koin dari Kaggle
- **Jumlah Kelas**: 4 (Koin Rp 100, Rp 200, Rp 500, Rp 1000)
- **Jumlah Gambar**: ~150-200 gambar per kelas
- **Kondisi**: Berbagai sudut, pencahayaan, dan latar belakang (lantai, tangan)
- **Preprocessing**: Ukuran gambar 512×512, maksimal 150 gambar per kelas untuk penyeimbangan

## Pipeline

```
Gambar Input (512x512)
    ↓
Edge Detection (Canny/Sobel)
    ↓
Hough Circle Transform
    ↓
Circular Segmentation (Original) ───┬── Feature Extraction (35 features)
    ↓                               │
Potong ke Diameter Lingkaran        │
    ↓                               │
Ubah Ukuran ke 512x512 (Dipotong) ─┴── Ekstraksi Fitur (35 fitur)
    ↓
Gabungkan Fitur (70 total)
    ↓
StandardScaler Normalization
    ↓
ML Classifier (Random Forest / SVM)
    ↓
Prediction
```

## Feature Engineering

### **Total Fitur: 70 fitur (Hybrid)**

Fitur diekstrak dari **DUA versi** koin yang sama:

- **Segmentasi Original** (35 fitur): Mempertahankan informasi ukuran absolut
- **Dipotong & Diubah Ukuran** (35 fitur): Menormalkan pola tekstur

### **Rincian Fitur per Versi (masing-masing 35 fitur)**

#### **A. FITUR TEKSTUR dari Deteksi Tepi (12 fitur)**

**1. Edge Density (1 feature)**

- **Apa itu?** Persentase pixel yang merupakan edge (garis tepi) dari total gambar
- **Cara hitung:** Jumlah pixel putih di edge detection ÷ total pixel
- **Mengapa penting?** Koin dengan detail lebih banyak (Rp 1000) akan memiliki edge density lebih tinggi dibanding koin polos (Rp 100)

**2. Edge Statistics (3 features)**

- **Edge Mean**: Rata-rata intensitas edge (0-255)
- **Edge Std**: Standar deviasi intensitas edge (variasi brightness edge)
- **Edge Max**: Nilai maksimum intensitas edge
- **Mengapa penting?** Koin dengan embossing dalam memiliki edge yang lebih tajam (nilai tinggi)

**3. Edge Histogram (8 features)**

- **Apa itu?** Distribusi intensitas edge dibagi menjadi 8 bin (rentang)
- **Cara hitung:** Hitung berapa banyak pixel di setiap rentang intensitas (0-32, 33-64, ..., 225-255)
- **Mengapa penting?** Setiap koin punya pola distribusi edge yang unik seperti "sidik jari"

#### **B. SHAPE FEATURES dari Hough Circle (4 features)**

**4. Normalized Radius (1 feature)**

- **Apa itu?** Ukuran radius lingkaran koin dibagi dengan ukuran gambar
- **Cara hitung:** radius ÷ max(tinggi, lebar gambar)
- **Mengapa penting?** Meskipun semua koin berbentuk bulat, ada variasi kecil ukuran relatif

**5. Center Position (2 features)**

- **Center X**: Posisi horizontal pusat koin (0.0 - 1.0)
- **Center Y**: Posisi vertical pusat koin (0.0 - 1.0)
- **Mengapa penting?** Informasi tambahan untuk normalisasi posisi koin dalam frame

**6. Circularity Score (1 feature)**

- **Apa itu?** Seberapa bulat koin yang terdeteksi (0 = tidak bulat, 1 = lingkaran sempurna)
- **Rumus:** (4π × Area) ÷ (Perimeter²)
- **Mengapa penting?** Koin yang terdistorsi atau miring akan memiliki circularity lebih rendah

#### **C. EDGE PATTERN FEATURES (12 features)**

**7. Edge Orientation Histogram (8 features)**

- **Apa itu?** Distribusi arah edge (0°, 45°, 90°, 135°, dll) dalam 8 bin
- **Cara hitung:** Hitung arah gradient (atas-bawah, kiri-kanan, diagonal) menggunakan arctan2
- **Mengapa penting?** Setiap koin punya pola arah edge yang berbeda:
  - Rp 100: Edge circular dominan
  - Rp 1000: Edge kompleks dengan berbagai arah (angka, teks, gambar Garuda)

**8. Gradient Statistics (4 features)**

- **Gradient Mean**: Rata-rata kekuatan perubahan intensitas
- **Gradient Std**: Variasi kekuatan gradient
- **Gradient Percentile 75**: Nilai gradient di persentil ke-75 (75% data di bawahnya)
- **Gradient Percentile 90**: Nilai gradient di persentil ke-90 (hanya 10% data lebih tinggi)
- **Mengapa penting?** Koin dengan relief dalam (embossing tinggi) memiliki gradient lebih kuat

#### **D. SPATIAL FEATURES - Quadrant Analysis (4 features)**

**9. Edge Density per Quadrant (4 features)**

- **Apa itu?** Gambar dibagi 4 bagian (atas-kiri, atas-kanan, bawah-kiri, bawah-kanan), hitung edge density masing-masing
- **Cara hitung:** Edge density di setiap kuadran
- **Mengapa penting?** Distribusi edge berbeda per koin:
  - Koin dengan angka besar di tengah: edge density tinggi di tengah
  - Koin dengan teks melingkar: edge density merata di tepi

#### **E. LOCAL TEXTURE FEATURES (3 features)**

**10. Local Variance Statistics (3 features)**

- **Variance Mean**: Rata-rata variasi intensitas di area lokal (5×5 pixel)
- **Variance Std**: Standar deviasi dari local variance
- **Variance Percentile 75**: Nilai variance di persentil ke-75
- **Cara hitung:** Sliding window 5×5 pixel, hitung variance di setiap window
- **Mengapa penting?** Mengukur tekstur halus vs kasar:
  - Koin dengan permukaan halus: variance rendah
  - Koin dengan tekstur kompleks (ukiran detail): variance tinggi

### **TOTAL FEATURES: 1 + 3 + 8 + 4 + 12 + 4 + 3 = 35 features**

### **Mengapa 35 Features Cukup untuk Membedakan 4 Koin?**

1. **Kombinasi Multi-Dimensional**:

   - 35 features menciptakan ruang 35-dimensi
   - Setiap koin punya "posisi" unik di ruang ini

2. **Redundancy & Robustness**:

   - Beberapa features overlap (saling mendukung)
   - Jika 1 feature gagal, ada features lain yang backup

3. **Machine Learning Magic**:

   - Random Forest belajar kombinasi features mana yang paling penting
   - Tidak semua 41 features digunakan dengan bobot sama

4. **Feature Importance**:
   - Model secara otomatis memberi bobot lebih tinggi ke features yang paling diskriminatif
   - Contoh: Edge orientation histogram mungkin lebih penting dari center position

## Hasil Eksperimen

### **Perbandingan Edge Detection**

| Method | Average Accuracy |
| ------ | ---------------- |
| Canny  | 0.7654           |
| Sobel  | 0.8248           |

**Winner: Sobel** (selisih +0.0594)

#### **Alasan Sobel Lebih Baik:**

**a. Resolusi lebih tinggi (512x512):** Dengan resolusi tinggi, Sobel dapat menangkap gradient detail yang lebih baik dibanding pada resolusi rendah (128x128)

**b. Texture-rich features:** Sobel menghasilkan gradient magnitude yang lebih kaya informasi untuk texture features pada koin

**c. Robust terhadap variasi pencahayaan:** Gradient Sobel lebih stabil terhadap perubahan brightness dan shadow pada dataset koin

**d. Thickness control:** Edge dari Sobel lebih tebal, memberikan informasi spatial yang lebih kaya untuk feature extraction

**e. Multi-scale information:** Sobel mempertahankan informasi gradual yang penting untuk membedakan detail emboss pada koin

#### **Catatan Penting:**

- Pada resolusi rendah (128x128), Canny lebih baik karena edge tipis
- Pada resolusi tinggi (512x512), Sobel unggul karena detail gradient
- Dataset balanced (150 images/class) mengurangi bias

### **Perbandingan Classifier**

| Classifier    | Average Accuracy |
| ------------- | ---------------- |
| Random Forest | 0.8201           |
| SVM           | 0.7701           |

**Winner: Random Forest** (selisih +0.0501)

### **BREAKTHROUGH: Hybrid Feature Extraction**

Setelah eksperimen awal, kami melakukan perbaikan dengan **Hybrid Approach**:

#### **Konsep Hybrid Features:**

- **Segmentasi Original** (35 fitur): Mempertahankan informasi ukuran absolut
- **Versi Dipotong** (35 fitur): Menormalkan tekstur/pola dengan pemotongan + pengubahan ukuran
- **Total**: **70 fitur** (35 original + 35 dipotong)

#### **Mengapa Hybrid Berhasil?**

1. **Informasi Ganda:**

   - Fitur original → Diskriminasi ukuran (Rp 1000 lebih besar dari Rp 100)
   - Fitur dipotong → Konsistensi tekstur (semua koin dinormalisasi ke skala sama)

2. **Complementary Strengths:**

   - Original: Bagus untuk pembedaan berbasis ukuran
   - Dipotong: Bagus untuk pembedaan berbasis tekstur

3. **Keunggulan Random Forest:**
   - Menangani data berdimensi tinggi (70 fitur) tanpa overfitting
   - Pemilihan kepentingan fitur otomatis

### **Model Terbaik (DIPERBARUI)**

| Model                      | Features | Accuracy   | Improvement  |
| -------------------------- | -------- | ---------- | ------------ |
| **Random Forest + Hybrid** | 70       | **0.8822** | **NEW BEST** |
| Random Forest + Sobel      | 35       | 0.8457     | -3.65%       |

### **Hasil Lengkap Semua Kombinasi**

| Model                      | Method             | Classifier    | Features | Accuracy   |
| -------------------------- | ------------------ | ------------- | -------- | ---------- |
| **Random Forest + Hybrid** | Hybrid (Orig+Crop) | Random Forest | 70       | **0.8822** |
| Random Forest + Sobel      | Sobel              | Random Forest | 35       | 0.8457     |
| SVM + Sobel                | Sobel              | SVM           | 35       | 0.8040     |
| Random Forest + Canny      | Canny              | Random Forest | 35       | 0.7946     |
| SVM + Canny                | Canny              | SVM           | 35       | 0.7362     |

### **Rincian Performa Model Hybrid**

| Class        | Precision | Recall | F1-Score | Support |
| ------------ | --------- | ------ | -------- | ------- |
| Rp 100       | 0.87      | 0.90   | 0.89     | 240     |
| Rp 1000      | 0.94      | 0.82   | 0.88     | 239     |
| Rp 200       | 0.85      | 0.94   | 0.89     | 240     |
| Rp 500       | 0.88      | 0.87   | 0.87     | 240     |
| **Accuracy** |           |        | **0.88** | 959     |

**Peningkatan Utama:**

- Skor F1 Rp 1000: 0.84 → **0.88** (+4.8%)
- Skor F1 Rp 200: 0.85 → **0.89** (+4.7%)
- Akurasi keseluruhan: **+3.65%**

## Kesimpulan

### **1. Perbaikan yang Diterapkan**

**a. IMAGE SIZE:** Diperbesar dari 128x128 ke **512x512** (4x lipat)

- Memberikan detail edge yang lebih baik
- Meningkatkan kualitas feature extraction

**b. DATASET BALANCING:** Limit **150 images per class**

- Mengurangi ketidakseimbangan data (dari selisih 500+ ke ~balanced)
- Mencegah overfitting pada kelas dengan data banyak

**c. CIRCLE DETECTION FILTER:** Hanya proses gambar dengan circle terdeteksi

- Meningkatkan kualitas data training
- Menghilangkan noise dari gambar yang gagal segmentation

### **2. Data Augmentation**

- **Rotasi**: 90°, 180°, 270°
- **Flip**: horizontal dan vertical
- **Brightness**: adjustment terang dan gelap
- **Total**: **8x data augmentation** per gambar original

### **3. Analisis Kesalahan Model**

#### **Interpretasi Confusion Matrix:**

- **FP dan FN merata** di seluruh kelas → Model **TIDAK overfit**
- Jika model overfit, biasanya 1-2 kelas tertentu akan memiliki performa sangat buruk
- Distribusi error yang merata menunjukkan model **generalisasi dengan baik**
- Tidak ada class bias yang signifikan

#### **Karakteristik Gambar yang Sulit:**

Gambar yang salah diprediksi biasanya:

- Pencahayaan ekstrem (terlalu terang/gelap)
- Sudut pengambilan yang tidak standar
- Koin terlalu kecil atau terlalu besar dalam frame
- Background yang kompleks atau mirip dengan warna koin
- Kualitas edge detection yang kurang optimal pada kondisi tersebut
