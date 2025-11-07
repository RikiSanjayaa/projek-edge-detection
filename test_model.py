"""
Coin classifier tester with HYBRID feature extraction (Original + Cropped).

This uses the best performing model: Random Forest + Hybrid Features (88.22% accuracy)

Usage:
    python test_model.py path/to/coin_image.jpg
    python test_model.py path/to/coin_image.jpg --save-steps
    python test_model.py path/to/coin_image.jpg --output result.json
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import cv2
import pickle
import json
import matplotlib.pyplot as plt

from preprocessing import (
    detect_and_segment_coin,
    extract_coin_features,
    extract_hybrid_features,
    crop_coin_to_circle,
    apply_sobel_edge,
    draw_circle_on_image
)


class CoinClassifierTester:
    """Coin classifier tester with hybrid feature extraction"""
    
    def __init__(self, model_dir='models'):
        self.model_dir = Path(model_dir)
        self.IMAGE_SIZE = (512, 512)
        self.class_names = ['Koin Rp 100', 'Koin Rp 1000', 'Koin Rp 200', 'Koin Rp 500']
        
    def load_model(self):
        """Load trained hybrid model"""
        model_path = self.model_dir / "random_forest_hybrid_model.pkl"
        scaler_path = self.model_dir / "random_forest_hybrid_scaler.pkl"
        model_name = "Random Forest + Hybrid (Original + Cropped)"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler not found: {scaler_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        return model, scaler, model_name
    
    def predict(self, image_path, save_steps=False, verbose=True):
        """
        Predict coin class with optional step-by-step visualization
        
        Args:
            image_path: Path to coin image
            save_steps: Save preprocessing steps as images
            verbose: Print detailed information
        
        Returns:
            dict with prediction results and preprocessing steps
        """
        # Load and resize image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        img_resized = cv2.resize(img, self.IMAGE_SIZE)
        
        # Load model
        model, scaler, model_name = self.load_model()
        
        if verbose:
            print("="*70)
            print("COIN CLASSIFICATION - PREDICTION")
            print("="*70)
            print(f"\nImage: {Path(image_path).name}")
            print(f"Model: {model_name}")
            print(f"Size: {self.IMAGE_SIZE}")
        
        # Step 1: Original segmentation
        segmented_original, circle_info, edges_original = detect_and_segment_coin(img_resized, 'sobel')
        
        # Step 2: Draw circle
        img_with_circle = draw_circle_on_image(img_resized, circle_info)
        
        if circle_info is None:
            print("\n[WARNING] Coin not detected!")
        else:
            if verbose:
                x, y, r = circle_info
                print(f"\n[OK] Coin detected: center=({x},{y}), radius={r}px")
        
        # Step 3: Hybrid Feature Extraction (Original + Cropped)
        cropped = crop_coin_to_circle(segmented_original, circle_info, self.IMAGE_SIZE)
        edges_cropped = apply_sobel_edge(cropped)
        
        features = extract_hybrid_features(
            segmented_original, cropped,
            edges_original, edges_cropped,
            circle_info
        )
        
        if verbose:
            print(f"Features extracted: {len(features)} hybrid features (35 original + 35 cropped)")
        
        # Step 4: Prediction
        features_scaled = scaler.transform(features.reshape(1, -1))
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        predicted_class = self.class_names[prediction]
        confidence = probabilities[prediction]
        
        # Display results
        if verbose:
            print("\n" + "="*70)
            print("PREDICTION RESULT")
            print("="*70)
            print(f"\nPredicted: {predicted_class}")
            print(f"Confidence: {confidence*100:.2f}%")
            print("\nProbabilities:")
            print("-" * 50)
            
            for idx, prob in sorted(enumerate(probabilities), key=lambda x: x[1], reverse=True):
                bar = '█' * int(prob * 40) + '░' * (40 - int(prob * 40))
                marker = ' <-- PREDICTED' if idx == prediction else ''
                print(f"  {self.class_names[idx]:15s} | {bar} | {prob*100:5.2f}%{marker}")
            
            print("\n" + "="*70)
        
        # Save preprocessing steps
        if save_steps:
            self._save_preprocessing_steps_hybrid(
                img_resized, edges_original, img_with_circle, 
                segmented_original, cropped,
                Path(image_path).stem
            )
        
        # Return results
        return {
            'predicted_class': predicted_class,
            'predicted_index': int(prediction),
            'confidence': float(confidence),
            'probabilities': {
                self.class_names[i]: float(probabilities[i]) 
                for i in range(len(self.class_names))
            },
            'circle_detected': circle_info is not None,
            'circle_info': {
                'x': int(circle_info[0]),
                'y': int(circle_info[1]),
                'radius': int(circle_info[2])
            } if circle_info else None,
            'preprocessing_steps': {
                'original': img_resized,
                'edges': edges_original,
                'circle_detection': img_with_circle,
                'segmented': segmented_original,
                'cropped': cropped
            },
            'num_features': len(features)
        }
    
    def _save_preprocessing_steps_hybrid(self, original, edges, circle_img, segmented, cropped, filename):
        """Save preprocessing steps for hybrid model (includes cropped version)"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Original
        axes[0, 0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('1. Original Image', fontsize=11, fontweight='bold')
        axes[0, 0].axis('off')
        
        # Edge Detection
        axes[0, 1].imshow(edges, cmap='gray')
        axes[0, 1].set_title('2. Sobel Edge Detection', fontsize=11, fontweight='bold')
        axes[0, 1].axis('off')
        
        # Circle Detection
        axes[0, 2].imshow(cv2.cvtColor(circle_img, cv2.COLOR_BGR2RGB))
        axes[0, 2].set_title('3. Hough Circle Detection', fontsize=11, fontweight='bold')
        axes[0, 2].axis('off')
        
        # Segmentation (Original)
        axes[1, 0].imshow(cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB))
        axes[1, 0].set_title('4. Segmented (Original)', fontsize=11, fontweight='bold')
        axes[1, 0].axis('off')
        
        # Cropped & Resized
        if cropped is not None:
            axes[1, 1].imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
            axes[1, 1].set_title('5. Cropped & Resized\n(Normalized Scale)', fontsize=11, fontweight='bold')
        else:
            axes[1, 1].text(0.5, 0.5, 'No cropped version', ha='center', va='center')
            axes[1, 1].set_title('5. Cropped (N/A)', fontsize=11, fontweight='bold')
        axes[1, 1].axis('off')
        
        # Feature Extraction Info
        axes[1, 2].axis('off')
        info_text = "HYBRID FEATURES\n\n"
        info_text += "• Original: 35 features\n"
        info_text += "  - Preserves size info\n"
        info_text += "  - Absolute radius\n"
        info_text += "  - Position data\n\n"
        info_text += "• Cropped: 35 features\n"
        info_text += "  - Normalized texture\n"
        info_text += "  - Consistent scale\n"
        info_text += "  - Pattern focus\n\n"
        info_text += "Total: 70 features"
        
        axes[1, 2].text(0.1, 0.5, info_text,
                       fontsize=10,
                       verticalalignment='center',
                       family='monospace',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.suptitle(f'Hybrid Preprocessing Steps: {filename}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_path = Path(f'preprocessing_steps_hybrid_{filename}.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n[OK] Hybrid preprocessing steps saved: {output_path}")


def main():
    """Main CLI"""
    parser = argparse.ArgumentParser(
        description='Coin classifier tester with Hybrid or Sobel model (Best: Hybrid 88.22%)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_model.py coin.jpg                           # Basic prediction
  python test_model.py coin.jpg --save-steps              # Save visualization
  python test_model.py coin.jpg --output result.json      # Export to JSON
  python test_model.py coin.jpg --quiet                   # Quiet mode
        """
    )
    
    parser.add_argument('image', type=str, help='Path to coin image')
    parser.add_argument('--model-dir', type=str, default='models',
                        help='Model directory (default: models)')
    parser.add_argument('--save-steps', action='store_true',
                        help='Save preprocessing steps visualization')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Save result to JSON file')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode')
    
    args = parser.parse_args()
    
    # Validate image
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    # Initialize and predict
    tester = CoinClassifierTester(model_dir=args.model_dir)
    
    try:
        result = tester.predict(
            image_path=image_path,
            save_steps=args.save_steps,
            verbose=not args.quiet
        )
        
        # Remove numpy arrays from result before JSON serialization
        if args.output:
            json_result = {k: v for k, v in result.items() if k != 'preprocessing_steps'}
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Result saved: {output_path}")
        
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTrain model first using coin-classification.ipynb")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
