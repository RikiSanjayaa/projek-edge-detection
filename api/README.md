# Coin Classification API

FastAPI backend for Indonesian coin classification using CNN and Random Forest models.

## Features

- **POST /predict** - Classify coin images
- Returns preprocessing step images (base64)
- Dual model predictions (CNN + Random Forest)
- Processing time metrics

## Prerequisites

- Python 3.10+
- Trained models in `../models/` directory

## Setup

### 1. Create Virtual Environment

```bash
# From project root (projek-edge-detection/)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and edit as needed:

```bash
cp api/.env.example api/.env
```

Edit `api/.env`:

```env
# Server Configuration
HOST=0.0.0.0          # Use 0.0.0.0 to allow external connections
PORT=8000             # API port

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://YOUR_SERVER_IP:5173
```

### 4. Ensure Models Exist

The API requires trained models in the `models/` directory:

```
models/
├── coin_classifier_cnn_8class.keras      # CNN model (required)
├── coin_classifier_8class_model.pkl      # Random Forest model (optional)
└── coin_classifier_8class_scaler.pkl     # RF scaler (optional)
```

**See [Models Section](#getting-the-models) below for how to get these files.**

### 5. Run the Server

```bash
# From project root
cd projek-edge-detection

# Activate venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# Run API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Or for production:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

```bash
GET /
GET /health
```

### Predict Coin

```bash
POST /predict
Content-Type: multipart/form-data

file: <image file>
```

**Response:**

```json
{
  "preprocessing_steps": {
    "original": "<base64>",
    "resized": "<base64>",
    "clahe": "<base64>",
    "sobel": "<base64>",
    "hough_circle": "<base64>",
    "cropped": "<base64>",
    "edge_final": "<base64>"
  },
  "circle_detected": true,
  "predictions": {
    "cnn": {
      "label": "Koin Rp 1000 - angka",
      "confidence": 0.95,
      "processing_time_ms": 150.5,
      "all_classes": [...]
    },
    "random_forest": {
      "label": "Koin Rp 1000 - angka",
      "confidence": 0.85,
      "processing_time_ms": 5.2,
      "all_classes": [...]
    }
  }
}
```

## Getting the Models

### Option 1: Copy from Trained Machine (Recommended)

If you've already trained the models on another machine, simply copy the `models/` folder:

```bash
# On your development machine, zip the models
cd projek-edge-detection
zip -r models.zip models/

# Transfer to server (using scp, rsync, or USB)
scp models.zip user@your-server:/path/to/projek-edge-detection/

# On server, extract
cd /path/to/projek-edge-detection
unzip models.zip
```

**Required files:**

- `coin_classifier_cnn_8class.keras` (~5-10 MB) - **Required**
- `coin_classifier_8class_model.pkl` (~1 MB) - Optional (for RF predictions)
- `coin_classifier_8class_scaler.pkl` (~1 KB) - Optional (for RF predictions)

### Option 2: Train from Notebook

Run the training notebook:

```bash
jupyter notebook notebooks/coin-classification-cnn.ipynb
```

This requires the dataset to be present.

## Environment Variables

| Variable       | Default                                       | Description                            |
| -------------- | --------------------------------------------- | -------------------------------------- |
| `HOST`         | `0.0.0.0`                                     | Server bind address                    |
| `PORT`         | `8000`                                        | Server port                            |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins (comma-separated) |

## Troubleshooting

### "Model not found" error

Make sure the models exist in `../models/` relative to the `api/` directory:

```
projek-edge-detection/
├── api/
│   └── main.py
└── models/
    └── coin_classifier_cnn_8class.keras  ← Must exist here
```

### CORS errors

Update `CORS_ORIGINS` in `api/.env` to include your frontend URL:

```env
CORS_ORIGINS=http://192.168.1.100:5173,http://your-domain.com
```
