from pydantic import BaseModel, Field

class BenchmarkMetrics(BaseModel):
    model1_map50: float = Field(..., example=0.892, description="Model 1 YOLO mAP@0.5 on held-out RICO split")
    model2_auc: float = Field(..., example=0.941, description="Model 2 Siamese pairwise state drift AUC")
    model3_spearman: float = Field(..., example=0.874, description="Model 3 Spearman correlation vs human friction ratings")
    model4_regression_detection_rate: float = Field(..., example=0.965, description="Model 4 Regression detection accuracy on injected fault suite")
    failure_memory_speedup_percent: float = Field(..., example=42.5, description="Percentage speedup after indexing 10 prior version runs")
