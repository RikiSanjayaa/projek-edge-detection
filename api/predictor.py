"""
Coin Prediction Module
Loads models and handles preprocessing + prediction
"""
import sys
import base64
from pathlib import Path
from io import BytesIO
import numpy as np
import cv2
from PIL import Image

# Add parent directory to path for importing preprocessing
sys.path.insert(0, str(Path(__file__).parent.parent))
from preprocessing import crop_coin_to_circle

# Lazy load models (loaded on first prediction)
_cnn_model = None
_rf_model = None
_rf_scaler = None
_class_names = None


def get_class_names():
    """Get class names for 8-class classification"""
    return [
        "Koin Rp 100 - angka",
        "Koin Rp 100 - gambar",
        "Koin Rp 1000 - angka",
        "Koin Rp 1000 - gambar",
        "Koin Rp 200 - angka",
        "Koin Rp 200 - gambar",
        "Koin Rp 500 - angka",
        "Koin Rp 500 - gambar",
    ]


def load_models():
    """Load CNN and Random Forest models"""
    global _cnn_model, _rf_model, _rf_scaler, _class_names
    
    models_dir = Path(__file__).parent.parent / "models"
    
    # Load CNN model
    if _cnn_model is None:
        try:
            from tensorflow import keras
            cnn_path = models_dir / "coin_classifier_cnn_8class.keras"
            if cnn_path.exists():
                _cnn_model = keras.models.load_model(cnn_path)
                print(f"✓ CNN model loaded from {cnn_path}")
            else:
                print(f"✗ CNN model not found at {cnn_path}")
        except Exception as e:
            print(f"✗ Error loading CNN model: {e}")
    
    # Load Random Forest model
    if _rf_model is None:
        try:
            import pickle
            rf_path = models_dir / "coin_classifier_8class_model.pkl"
            scaler_path = models_dir / "coin_classifier_8class_scaler.pkl"
            
            if rf_path.exists():
                with open(rf_path, 'rb') as f:
                    _rf_model = pickle.load(f)
                print(f"✓ RF model loaded from {rf_path}")
            
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    _rf_scaler = pickle.load(f)
                print(f"✓ RF scaler loaded from {scaler_path}")
        except Exception as e:
            print(f"✗ Error loading RF model: {e}")
    
    _class_names = get_class_names()
    
    return _cnn_model is not None or _rf_model is not None


def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply CLAHE normalization"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)


def apply_sobel_edge(image):
    """Apply Sobel edge detection"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply CLAHE first
    gray = apply_clahe(gray)
    
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_combined = np.uint8(sobel_combined / sobel_combined.max() * 255)
    return sobel_combined


def detect_circle(image):
    """Detect coin circle using Hough Transform"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=min(gray.shape) // 2
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        return circles[0, 0]  # Return first detected circle (x, y, radius)
    return None


def image_to_base64(image, format="PNG"):
    """Convert numpy image to base64 string"""
    if len(image.shape) == 2:
        # Grayscale
        pil_image = Image.fromarray(image)
    else:
        # BGR to RGB
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    buffer = BytesIO()
    pil_image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def resize_with_aspect_ratio(image, target_size=(256, 256)):
    """
    Resize image while maintaining aspect ratio by zooming to fit and center-cropping.
    This prevents circular coins from becoming oval when the input image is not square.
    
    Args:
        image: Input image (BGR or grayscale)
        target_size: Target (width, height) tuple
    
    Returns:
        Resized and center-cropped image with maintained aspect ratio
    """
    target_w, target_h = target_size
    h, w = image.shape[:2]
    
    # Calculate scale to fill target (zoom to fit, crop excess)
    scale = max(target_w / w, target_h / h)
    
    # New dimensions after scaling
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Resize with aspect ratio maintained
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Calculate crop offsets to center-crop to target size
    x_offset = (new_w - target_w) // 2
    y_offset = (new_h - target_h) // 2
    
    # Center-crop to target size
    cropped = resized[y_offset:y_offset + target_h, x_offset:x_offset + target_w]
    
    return cropped


def preprocess_image(image_bytes, image_size=(256, 256)):
    """
    Run full preprocessing pipeline and return step images
    
    Returns:
        steps: dict of preprocessing step images (base64)
        final_image: processed image ready for prediction
        circle_info: detected circle (x, y, radius) or None
    """
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    original = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if original is None:
        raise ValueError("Could not decode image")
    
    # Step 1: Resize with aspect ratio preservation (prevents circular coins from becoming oval)
    resized = resize_with_aspect_ratio(original, image_size)
    
    # Step 2: CLAHE
    clahe_img = apply_clahe(resized)
    
    # Step 3: Sobel Edge (on resized, before crop)
    sobel_img = apply_sobel_edge(resized)
    
    # Step 4: Hough Circle Detection
    circle = detect_circle(resized)
    
    hough_img = resized.copy()
    if circle is not None:
        x, y, r = circle
        cv2.circle(hough_img, (x, y), r, (0, 255, 0), 3)
        cv2.circle(hough_img, (x, y), 3, (0, 0, 255), -1)
    
    # Step 5: Crop to circle
    if circle is not None:
        # Segment first
        mask = np.zeros(resized.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (circle[0], circle[1]), circle[2], 255, -1)
        segmented = cv2.bitwise_and(resized, resized, mask=mask)
        
        # Crop
        cropped = crop_coin_to_circle(segmented, tuple(circle), image_size)
    else:
        cropped = resized.copy()
    
    # Step 6: Final edge detection on cropped
    final_edge = apply_sobel_edge(cropped)
    
    # Collect all steps as base64
    steps = {
        "original": image_to_base64(original),
        "resized": image_to_base64(resized),
        "clahe": image_to_base64(clahe_img),
        "sobel": image_to_base64(sobel_img),
        "hough_circle": image_to_base64(hough_img),
        "cropped": image_to_base64(cropped),
        "edge_final": image_to_base64(final_edge),
    }
    
    return steps, final_edge, circle


def extract_features(image, edges, circle_info):
    """Extract 35 features for Random Forest (simplified version)"""
    features = []
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Edge features (12)
    edge_density = np.sum(edges > 0) / edges.size
    features.append(edge_density)
    features.extend([np.mean(edges), np.std(edges), np.max(edges)])
    
    edge_hist, _ = np.histogram(edges.flatten(), bins=8, range=(0, 256))
    edge_hist = edge_hist / (edge_hist.sum() + 1e-6)
    features.extend(edge_hist)
    
    # Shape features (4)
    if circle_info is not None:
        x, y, r = circle_info
        features.append(r / max(gray.shape))
        features.extend([x / gray.shape[1], y / gray.shape[0]])
        features.append(1.0)  # circularity placeholder
    else:
        features.extend([0, 0, 0, 0])
    
    # Edge pattern features (12)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    direction = np.arctan2(sobel_y, sobel_x)
    
    orient_hist, _ = np.histogram(direction[magnitude > magnitude.mean()], bins=8, range=(-np.pi, np.pi))
    orient_hist = orient_hist / (orient_hist.sum() + 1e-6)
    features.extend(orient_hist)
    features.extend([np.mean(magnitude), np.std(magnitude), np.percentile(magnitude, 75), np.percentile(magnitude, 90)])
    
    # Spatial features (4)
    h, w = edges.shape
    quadrants = [edges[0:h//2, 0:w//2], edges[0:h//2, w//2:w], edges[h//2:h, 0:w//2], edges[h//2:h, w//2:w]]
    for quad in quadrants:
        features.append(np.sum(quad > 0) / quad.size if quad.size > 0 else 0)
    
    # Texture features (3)
    kernel_size = 5
    local_mean = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
    local_var = cv2.blur((gray.astype(float) - local_mean)**2, (kernel_size, kernel_size))
    features.extend([np.mean(local_var), np.std(local_var), np.percentile(local_var, 75)])
    
    return np.array(features, dtype=np.float32)


def predict(image_bytes):
    """
    Main prediction function
    
    Returns dict with:
        - preprocessing_steps: base64 images of each step
        - predictions: results from CNN and RF
        - circle_detected: bool
    """
    import time
    
    # Ensure models are loaded
    load_models()
    
    # Run preprocessing
    steps, final_edge, circle = preprocess_image(image_bytes)
    
    result = {
        "preprocessing_steps": steps,
        "circle_detected": circle is not None,
        "predictions": {}
    }
    
    # CNN Prediction
    if _cnn_model is not None:
        try:
            start_time = time.time()
            
            # Prepare input (normalize to 0-1, add batch and channel dims)
            cnn_input = final_edge.astype(np.float32) / 255.0
            cnn_input = np.expand_dims(cnn_input, axis=(0, -1))  # (1, 256, 256, 1)
            
            # Predict
            proba = _cnn_model.predict(cnn_input, verbose=0)[0]
            pred_idx = np.argmax(proba)
            
            elapsed = time.time() - start_time
            
            result["predictions"]["cnn"] = {
                "label": _class_names[pred_idx],
                "confidence": float(proba[pred_idx]),
                "processing_time_ms": round(elapsed * 1000, 2),
                "all_classes": [
                    {"label": _class_names[i], "confidence": float(proba[i])}
                    for i in range(len(_class_names))
                ]
            }
        except Exception as e:
            result["predictions"]["cnn"] = {"error": str(e)}
    
    # Random Forest Prediction
    if _rf_model is not None and _rf_scaler is not None:
        try:
            start_time = time.time()
            
            # Extract features
            # For cropped, circle is centered
            h, w = final_edge.shape
            circle_cropped = (w//2, h//2, min(w, h)//2)
            features = extract_features(final_edge, final_edge, circle_cropped)
            
            # Scale and predict
            features_scaled = _rf_scaler.transform(features.reshape(1, -1))
            pred_idx = _rf_model.predict(features_scaled)[0]
            proba = _rf_model.predict_proba(features_scaled)[0]
            
            elapsed = time.time() - start_time
            
            result["predictions"]["random_forest"] = {
                "label": _class_names[pred_idx],
                "confidence": float(proba[pred_idx]),
                "processing_time_ms": round(elapsed * 1000, 2),
                "all_classes": [
                    {"label": _class_names[i], "confidence": float(proba[i])}
                    for i in range(len(_class_names))
                ]
            }
        except Exception as e:
            result["predictions"]["random_forest"] = {"error": str(e)}
    
    return result
