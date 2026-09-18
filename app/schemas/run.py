from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class DetectedElement(BaseModel):
    id: int
    bbox: BoundingBox
    element_class: str = Field(default="control", alias="class")
    confidence: float
    center_x: int
    center_y: int

    class Config:
        populate_by_name = True

class StepEvent(BaseModel):
    step_number: int
    action_type: str  # click, type, scroll, wait
    target_coordinates: Optional[Dict[str, int]] = None
    target_element_class: Optional[str] = None
    screenshot_base64: Optional[str] = None
    visual_drift_score: float = 0.0
    state_classification: str = "new_state" # same_state, new_state, drifted_duplicate
    instant_friction: float = 0.0
    timestamp: float

class RunRequest(BaseModel):
    goal: str = Field(..., example="Filter for blue shoes and complete checkout")
    target_url: Optional[str] = Field(default=None, example="http://localhost:8000/mock_apps/sample_ecommerce/v1_good.html")
    url: Optional[str] = Field(default=None, example="http://localhost:8000/mock_apps/sample_ecommerce/v1_good.html")
    platform: str = Field(default="chrome", example="chrome")

    @property
    def resolved_target_url(self) -> str:
        return self.target_url or self.url or "http://localhost:8000/mock_apps/sample_ecommerce/v1_good.html"

class RunResponse(BaseModel):
    run_id: str

class FailureMemoryStats(BaseModel):
    runs_seen: int
    detection_speed_curve: List[float]
    recall_accuracy: float
