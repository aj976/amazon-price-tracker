from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

from services.tracker import track_product
from database import db
from utils.parser import is_valid_amazon_url

# Setup FastAPI App
app = FastAPI(title="Amazon Price Tracker API")

# Setup CORS to allow the React Frontend to hit it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductRequest(BaseModel):
    url: str
    target_price: float

@app.post("/api/track")
def add_product(req: ProductRequest):
    """
    Endpoint for React to add a new tracking rule.
    """
    if not is_valid_amazon_url(req.url):
        raise HTTPException(status_code=400, detail="Invalid Amazon URL provided.")
        
    result = track_product(req.url, req.target_price)
    if result.get("success"):
        return {"success": True, "message": result.get("message"), "data": result.get("data")}
    else:
        raise HTTPException(status_code=500, detail=result.get("message"))

@app.get("/api/products")
def list_products():
    """
    Endpoint for React to fetch all tracked products and their statuses.
    """
    items = db.get_all_tracked_products()
    return {"success": True, "data": items if items else []}

@app.delete("/api/products/{asin}")
def remove_product(asin: str):
    """
    Endpoint to remove a product from tracking.
    """
    db_client = db.get_db()
    if not db_client:
        raise HTTPException(status_code=500, detail="Database connection error.")
        
    product = db.get_product_by_asin(asin)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
        
    try:
        db_client.table("products").delete().eq("id", product["id"]).execute()
        return {"success": True, "message": f"Successfully removed {asin}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
