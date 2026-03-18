from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from database.repository import Repository
from api.deps import get_repository

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductItem(BaseModel):
    id: int
    asin: str
    title: str
    url: str

class TrackedProductResponse(BaseModel):
    id: int
    product_id: int
    target_price: float
    last_notified_price: Optional[float]
    products: Optional[ProductItem]

class ProductListResponse(BaseModel):
    success: bool
    data: List[dict]

class GeneralResponse(BaseModel):
    success: bool
    message: str

@router.get("", response_model=ProductListResponse)
def list_products(repo: Repository = Depends(get_repository)):
    """Fetch all tracked products and their statuses."""
    try:
        items = repo.get_all_tracked_products()
        return ProductListResponse(success=True, data=items if items else [])
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@router.delete("/{asin}", response_model=GeneralResponse)
def remove_product(asin: str, repo: Repository = Depends(get_repository)):
    """Remove a product from tracking."""
    try:
        repo.delete_product(asin)
        return GeneralResponse(success=True, message=f"Successfully removed {asin}")
    except ValueError as ve:
        raise HTTPException(status_code=404, detail={"error": str(ve)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
