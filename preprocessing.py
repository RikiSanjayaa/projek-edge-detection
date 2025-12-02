"""
Preprocessing functions for coin classification.
Contains edge detection, circle detection, cropping, and feature extraction.
"""

import numpy as np
import cv2


def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    to normalize lighting variations across images.
    
    Args:
        image: Input image (BGR or grayscale)
        clip_limit: Threshold for contrast limiting (default 2.0)
        tile_grid_size: Size of grid for histogram equalization (default 8x8)
    
    Returns:
        Image with normalized contrast
    """
    if len(image.shape) == 3:
        # For color images, convert to LAB and apply CLAHE on L channel
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l_clahe = clahe.apply(l)
        
        lab_clahe = cv2.merge([l_clahe, a, b])
        result = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
    else:
        # For grayscale images, apply CLAHE directly
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        result = clahe.apply(image)
    
    return result


def resize_with_padding(image, target_size=(512, 512)):
    """
    Resize image dengan padding untuk mempertahankan aspect ratio.
    Menghindari distorsi pada gambar yang tidak kotak.
    
    Args:
        image: Input image (BGR)
        target_size: Target size (width, height)
    
    Returns:
        Resized image with padding (no distortion)
    """
    h, w = image.shape[:2]
    target_w, target_h = target_size
    
    # Hitung scale ratio
    scale = min(target_w / w, target_h / h)
    
    # Ukuran baru setelah scale
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Resize dengan aspect ratio preserved
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Buat canvas dengan padding (background hitam)
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    
    # Hitung posisi untuk center image
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    
    # Paste resized image ke canvas
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas


def apply_canny_edge(image, use_clahe=True):
    """Apply Canny edge detection
    
    Args:
        image: Input image (BGR or grayscale)
        use_clahe: Whether to apply CLAHE before edge detection (default True)
    
    Returns:
        Edge detection result
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply CLAHE to normalize lighting before edge detection
    if use_clahe:
        gray = apply_clahe(gray)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges


def apply_sobel_edge(image, use_clahe=True):
    """Apply Sobel edge detection
    
    Args:
        image: Input image (BGR or grayscale)
        use_clahe: Whether to apply CLAHE before edge detection (default True)
    
    Returns:
        Edge detection result
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply CLAHE to normalize lighting before edge detection
    if use_clahe:
        gray = apply_clahe(gray)
    
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_combined = np.uint8(sobel_combined / sobel_combined.max() * 255)
    
    return sobel_combined


def detect_and_segment_coin(image, edge_method='sobel', use_clahe=True):
    """
    Detect coin using Hough Circle Transform and segment it
    
    Args:
        image: Input image
        edge_method: 'canny' or 'sobel'
        use_clahe: Whether to apply CLAHE before edge detection (default True)
    
    Returns:
        segmented: Masked image focusing on coin region
        circle_info: (x, y, radius) of detected circle, or None
        edges: Edge detection result
    """
    # Edge detection (with optional CLAHE)
    if edge_method == 'canny':
        edges = apply_canny_edge(image, use_clahe=use_clahe)
    else:
        edges = apply_sobel_edge(image, use_clahe=use_clahe)
    
    # Convert to grayscale for Hough Transform
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Detect circles using Hough Transform
    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=200
    )
    
    segmented = image.copy()
    circle_info = None
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circle = circles[0, 0]
        x, y, radius = circle[0], circle[1], circle[2]
        circle_info = (x, y, radius)
        
        # Create circular mask
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        
        # Apply mask to image
        if len(image.shape) == 3:
            segmented = cv2.bitwise_and(image, image, mask=mask)
        else:
            segmented = cv2.bitwise_and(image, image, mask=mask)
    
    return segmented, circle_info, edges


def crop_coin_to_circle(image, circle_info, target_size=(512, 512)):
    """
    Crop image to circle diameter and resize to target size
    This normalizes coin scale across different coin sizes
    
    Args:
        image: Input image (segmented or original)
        circle_info: (x, y, radius) from Hough Circle Transform
        target_size: Target size after cropping (default 512x512)
    
    Returns:
        cropped_resized: Cropped and resized image to target size
    """
    if circle_info is None:
        # If no circle detected, return resized original
        return cv2.resize(image, target_size)
    
    x, y, radius = circle_info
    
    # Validate circle parameters
    if radius <= 0 or x < 0 or y < 0:
        return cv2.resize(image, target_size)
    
    # Define bounding box around circle
    # Add small margin (5%) to ensure we capture full circle
    margin = int(radius * 0.05)
    x1 = max(0, x - radius - margin)
    y1 = max(0, y - radius - margin)
    x2 = min(image.shape[1], x + radius + margin)
    y2 = min(image.shape[0], y + radius + margin)
    
    # Ensure valid crop region (non-empty and has minimum size)
    min_crop_size = 10  # Minimum crop size to avoid too small images
    if x2 <= x1 or y2 <= y1 or (x2 - x1) < min_crop_size or (y2 - y1) < min_crop_size:
        # Invalid crop region, return resized original
        return cv2.resize(image, target_size)
    
    # Crop to bounding box
    cropped = image[y1:y2, x1:x2]
    
    # Check if cropped is empty or too small
    if cropped.size == 0 or cropped.shape[0] < min_crop_size or cropped.shape[1] < min_crop_size:
        return cv2.resize(image, target_size)
    
    # Resize to target size
    cropped_resized = cv2.resize(cropped, target_size)
    
    return cropped_resized


def extract_coin_features(segmented_image, edges, circle_info):
    """
    Extract comprehensive features from segmented coin (41 features)
    
    Args:
        segmented_image: Image after circle segmentation
        edges: Edge detection result
        circle_info: (x, y, radius) from Hough Circle, or None
    
    Returns:
        Feature vector (numpy array of 41 features)
    """
    features = []
    
    # Convert to grayscale if needed
    if len(segmented_image.shape) == 3:
        gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = segmented_image
    
    # --- 1. TEXTURE FEATURES (12 features) ---
    edge_density = np.sum(edges > 0) / edges.size
    features.append(edge_density)
    
    edge_mean = np.mean(edges)
    edge_std = np.std(edges)
    edge_max = np.max(edges)
    features.extend([edge_mean, edge_std, edge_max])
    
    edge_hist, _ = np.histogram(edges.flatten(), bins=8, range=(0, 256))
    edge_hist = edge_hist / (edge_hist.sum() + 1e-6)
    features.extend(edge_hist)
    
    # --- 2. SHAPE FEATURES (4 features) ---
    if circle_info is not None:
        x, y, radius = circle_info
        normalized_radius = radius / max(gray.shape)
        features.append(normalized_radius)
        
        center_x = x / gray.shape[1]
        center_y = y / gray.shape[0]
        features.extend([center_x, center_y])
        
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        masked_edges = cv2.bitwise_and(edges, edges, mask=mask)
        
        contours, _ = cv2.findContours(masked_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            if perimeter > 0:
                circularity = (4 * np.pi * area) / (perimeter**2 + 1e-6)
            else:
                circularity = 0
            features.append(circularity)
        else:
            features.append(0)
    else:
        features.extend([0, 0, 0, 0])
    
    # --- 3. EDGE PATTERN FEATURES (12 features) ---
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    direction = np.arctan2(sobel_y, sobel_x)
    
    orientation_hist, _ = np.histogram(
        direction[magnitude > magnitude.mean()],
        bins=8,
        range=(-np.pi, np.pi)
    )
    orientation_hist = orientation_hist / (orientation_hist.sum() + 1e-6)
    features.extend(orientation_hist)
    
    features.extend([
        np.mean(magnitude),
        np.std(magnitude),
        np.percentile(magnitude, 75),
        np.percentile(magnitude, 90)
    ])
    
    # --- 4. SPATIAL FEATURES (4 features) ---
    h, w = edges.shape
    quadrants = [
        edges[0:h//2, 0:w//2],
        edges[0:h//2, w//2:w],
        edges[h//2:h, 0:w//2],
        edges[h//2:h, w//2:w]
    ]
    
    for quad in quadrants:
        quad_density = np.sum(quad > 0) / quad.size if quad.size > 0 else 0
        features.append(quad_density)
    
    # --- 5. TEXTURE FEATURES (3 features) ---
    kernel_size = 5
    local_mean = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
    local_var = cv2.blur((gray.astype(float) - local_mean)**2, (kernel_size, kernel_size))
    
    features.extend([
        np.mean(local_var),
        np.std(local_var),
        np.percentile(local_var, 75)
    ])
    
    return np.array(features, dtype=np.float32)


def extract_hybrid_features(segmented_original, segmented_cropped, 
                           edges_original, edges_cropped, circle_info):
    """
    Extract hybrid features from both original segmentation and cropped version
    
    This approach combines:
    - Features from original segmentation (preserves absolute size info)
    - Features from cropped version (normalizes texture/pattern)
    
    Args:
        segmented_original: Original segmented image (with black background)
        segmented_cropped: Cropped and resized image (normalized scale)
        edges_original: Edge detection on original
        edges_cropped: Edge detection on cropped
        circle_info: (x, y, radius) from original image
    
    Returns:
        Combined feature vector (82 features total: 41 original + 41 cropped)
    """
    # Extract features from original (preserves size information)
    features_original = extract_coin_features(
        segmented_original, edges_original, circle_info
    )
    
    # Extract features from cropped (normalized texture/pattern)
    # Note: Use modified circle_info for cropped image (centered)
    if circle_info is not None:
        # After cropping and resizing, circle is centered
        h, w = segmented_cropped.shape[:2]
        circle_info_cropped = (w//2, h//2, min(w, h)//2)
    else:
        circle_info_cropped = None
    
    features_cropped = extract_coin_features(
        segmented_cropped, edges_cropped, circle_info_cropped
    )
    
    # Concatenate both feature sets
    features_hybrid = np.concatenate([features_original, features_cropped])
    
    return features_hybrid


def draw_circle_on_image(image, circle_info):
    """
    Draw circle detection result on image
    
    Args:
        image: Input image
        circle_info: (x, y, radius) tuple
    
    Returns:
        Image with circle drawn
    """
    img_with_circle = image.copy()
    if circle_info is not None:
        x, y, r = circle_info
        cv2.circle(img_with_circle, (x, y), r, (0, 255, 0), 3)
        cv2.circle(img_with_circle, (x, y), 2, (0, 0, 255), 5)
    return img_with_circle
