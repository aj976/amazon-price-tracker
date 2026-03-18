from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.tracking_service import TrackingService
from api.deps import get_tracking_service
from utils.parser import is_valid_amazon_url

router = APIRouter(prefix="/api/track", tags=["tracking"])

class TrackRequest(BaseModel):
    url: str
    target_price: float

class TrackResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@router.post("", response_model=TrackResponse)
def add_tracking_rule(req: TrackRequest, tracking_service: TrackingService = Depends(get_tracking_service)):
    """Add a new product to tracking list."""
    if not is_valid_amazon_url(req.url):
        raise HTTPException(status_code=400, detail={"error": "Invalid Amazon URL provided."})
        
    try:
        result = tracking_service.track_product(req.url, req.target_price)
        if result.get("success"):
            return TrackResponse(success=True, message=result.get("message"), data=result.get("data"))
        else:
            raise HTTPException(status_code=500, detail={"error": result.get("message")})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
