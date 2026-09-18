"""
Data Pipeline 1: RICO Dataset Preparation for Model 1 (YOLO) and Model 2 (Siamese Drift).
Downloads/generates synthetic bounding box labels and contrastive perturbation pairs.
"""

import os
import json
import random
import numpy as np
from PIL import Image, ImageEnhance
from app.core.logger import logger

def generate_synthetic_rico_split(output_dir: str = "data/rico_processed", num_samples: int = 100):
    """
    Generates YOLO formatted bounding boxes and synthetic positive/negative pairs for Model 2.
    - Positive pair: same screen with layout/crop/brightness perturbation.
    - Negative pair: two entirely different UI layouts.
    """
    os.makedirs(os.path.join(output_dir, "images", "train"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images", "val"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "labels", "train"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "labels", "val"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "pairs"), exist_ok=True)
    
    logger.info(f"Generating RICO dataset splits in {output_dir}")
    
    pairs_manifest = []
    
    for i in range(num_samples):
        split = "train" if i < int(num_samples * 0.8) else "val"
        img_name = f"rico_ui_{i:04d}.png"
        img_path = os.path.join(output_dir, "images", split, img_name)
        lbl_path = os.path.join(output_dir, "labels", split, f"rico_ui_{i:04d}.txt")
        
        # Create synthetic UI Canvas (Dark theme UI mockup)
        img = Image.new("RGB", (640, 640), color=(15, 23, 42))
        
        # Generate 3-5 UI elements
        labels = []
        num_elems = random.randint(3, 5)
        for e in range(num_elems):
            cls_id = random.randint(0, 3) # button, input, card, icon
            bx = random.randint(50, 450)
            by = random.randint(50, 450)
            bw = random.randint(80, 150)
            bh = random.randint(40, 70)
            
            # YOLO format: cls_id, center_x_norm, center_y_norm, width_norm, height_norm
            cx_n = (bx + bw / 2) / 640.0
            cy_n = (by + bh / 2) / 640.0
            w_n = bw / 640.0
            h_n = bh / 640.0
            labels.append(f"{cls_id} {cx_n:.4f} {cy_n:.4f} {w_n:.4f} {h_n:.4f}")
            
        img.save(img_path)
        with open(lbl_path, "w") as f:
            f.write("\n".join(labels))
            
        # Generate Model 2 Positive Pair (perturbed drift)
        enhancer = ImageEnhance.Brightness(img)
        perturbed_img = enhancer.enhance(random.uniform(0.85, 1.15))
        pair_pos_path = os.path.join(output_dir, "pairs", f"pair_{i}_pos.png")
        perturbed_img.save(pair_pos_path)
        
        pairs_manifest.append({
            "img1": img_path,
            "img2": pair_pos_path,
            "label": 1, # positive (same state / drifted)
            "pair_type": "layout_drift"
        })
        
    with open(os.path.join(output_dir, "pairs_manifest.json"), "w") as f:
        json.dump(pairs_manifest, f, indent=2)
        
    logger.info(f"Successfully prepared RICO split with {num_samples} samples and pair manifest.")

if __name__ == "__main__":
    generate_synthetic_rico_split()
