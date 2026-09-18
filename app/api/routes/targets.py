from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/targets", tags=["targets"])

TARGET_PRESETS = [
    {
        "id": "ecommerce_v1_baseline",
        "name": "ApexGear Athletic Footwear (v1 Baseline)",
        "url": "http://localhost:8000/mock_apps/sample_ecommerce/v1_good.html",
        "category": "E-Commerce",
        "description": "Clean baseline checkout flow with proper focus states and low friction."
    },
    {
        "id": "ecommerce_v2_regression",
        "name": "ApexGear Athletic Footwear (v2 Injected Regression)",
        "url": "http://localhost:8000/mock_apps/sample_ecommerce/v2_regression.html",
        "category": "E-Commerce",
        "description": "Regression build with sudden layout shifts, circular promo code loops, and occluded buttons."
    }
]

@router.get("", response_model=List[Dict[str, Any]])
async def get_target_presets():
    """
    GET /api/targets
    Returns the list of target application presets for quick testing and judging demo.
    """
    return TARGET_PRESETS
