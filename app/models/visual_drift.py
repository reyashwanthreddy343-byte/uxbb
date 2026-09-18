import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import numpy as np
from typing import Tuple
from app.core.logger import logger

class SiameseVisualDrift(nn.Module):
    """
    Model 2: Siamese Visual Diff / State Drift Classifier.
    Extracts deep visual embeddings and classifies whether two screenshots are:
    - same_state (cos_sim > 0.92)
    - drifted_duplicate (0.75 <= cos_sim <= 0.92) - e.g. cross-platform/layout shift
    - new_state (cos_sim < 0.75)
    """
    
    def __init__(self, embedding_dim: int = 128):
        super().__init__()
        self.embedding_dim = embedding_dim
        # Lightweight CNN feature extractor
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.projection_head = nn.Sequential(
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Linear(256, embedding_dim)
        )

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.encoder(x)
        feat = feat.view(feat.size(0), -1)
        emb = self.projection_head(feat)
        return F.normalize(emb, p=2, dim=1)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        emb1 = self.forward_once(x1)
        emb2 = self.forward_once(x2)
        return F.cosine_similarity(emb1, emb2)

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        img_resized = image.resize((224, 224)).convert("RGB")
        arr = np.array(img_resized, dtype=np.float32) / 255.0
        # Normalize
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        arr = (arr - mean) / std
        tensor = torch.tensor(arr).permute(2, 0, 1).unsqueeze(0).float()
        return tensor

    def compare_states(self, img1: Image.Image, img2: Image.Image) -> Tuple[float, str]:
        """Compares two screenshots and returns (similarity_score, state_verdict)."""
        t1 = self.preprocess_image(img1)
        t2 = self.preprocess_image(img2)
        with torch.no_grad():
            emb1 = self.forward_once(t1)
            emb2 = self.forward_once(t2)
            similarity = F.cosine_similarity(emb1, emb2).item()
            
        similarity = float(np.clip(similarity, 0.0, 1.0))
        if similarity > 0.92:
            verdict = "same_state"
        elif similarity >= 0.72:
            verdict = "drifted_duplicate"
        else:
            verdict = "new_state"
            
        return round(similarity, 4), verdict
