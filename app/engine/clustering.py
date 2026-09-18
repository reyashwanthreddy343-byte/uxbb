import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import DBSCAN
from app.core.logger import logger

class RootCauseClusterer:
    """
    Standout Feature #3: Root-Cause Clustering Engine.
    Clusters disparate UI friction symptoms and regression findings by spatial
    and step proximity into common root causes.
    """
    
    def cluster_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not findings or len(findings) == 0:
            return findings
            
        if len(findings) == 1:
            findings[0]["cluster_id"] = "cluster_root_1"
            return findings
            
        # Feature vector: normalized (x / 100, y / 100) spatial coordinates
        feature_matrix = []
        for f in findings:
            coords = f.get("coordinates") or {"x": 500, "y": 400}
            feature_matrix.append([
                coords.get("x", 500) / 100.0,
                coords.get("y", 400) / 100.0
            ])
            
        X = np.array(feature_matrix)
        
        # Spatial distance clustering: elements within ~50px are clustered together
        clustering = DBSCAN(eps=0.8, min_samples=1)
        labels = clustering.fit_predict(X)
        
        for i, f in enumerate(findings):
            f["cluster_id"] = f"cluster_root_{int(labels[i]) + 1}"
            
        num_clusters = len(set(labels))
        logger.info(f"Clustered {len(findings)} findings into {num_clusters} root cause groups.")
        return findings

root_cause_clusterer = RootCauseClusterer()
