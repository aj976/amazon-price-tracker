import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SupabaseClient:
    _instance = None
    client: Client | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("Warning: SUPABASE_URL and SUPABASE_KEY must be set in .env")
            self.client = None
            return
            
        self.client = create_client(url, key)

    def get_client(self) -> Client | None:
        return self.client

def get_db() -> Client | None:
    """Helper function to get the Supabase client instance."""
    return SupabaseClient().get_client()

# ==========================================
# Database Operations
# ==========================================

def insert_product(asin: str, title: str, url: str) -> dict | None:
    """Inserts a new product or ignores if ASIN already exists."""
    db = get_db()
    if not db: return None
    
    try:
        data, count = db.table("products").upsert(
            {"asin": asin, "title": title, "url": url}, 
            on_conflict="asin"
        ).execute()
        return data[1][0] if len(data[1]) > 0 else None
    except Exception as e:
        print(f"Error inserting product: {e}")
        return None

def get_product_by_asin(asin: str) -> dict | None:
    db = get_db()
    if not db: return None
    
    try:
        data, count = db.table("products").select("*").eq("asin", asin).execute()
        return data[1][0] if len(data[1]) > 0 else None
    except Exception as e:
        print(f"Error fetching product: {e}")
        return None

def store_price(product_id: int, price: float) -> bool:
    """Records a new price for the given product ID."""
    db = get_db()
    if not db: return False
    
    try:
        db.table("price_history").insert(
            {"product_id": product_id, "price": price}
        ).execute()
        return True
    except Exception as e:
        print(f"Error storing price: {e}")
        return False

def setup_tracking(product_id: int, target_price: float) -> bool:
    """Sets up or updates the target tracking price for a product."""
    db = get_db()
    if not db: return False
    
    try:
        # Check if tracking already exists
        response, count = db.table("tracking").select("*").eq("product_id", product_id).execute()
        
        if len(response[1]) > 0:
            # Update
            db.table("tracking").update({"target_price": target_price}).eq("product_id", product_id).execute()
        else:
            # Insert
            db.table("tracking").insert({"product_id": product_id, "target_price": target_price}).execute()
        return True
    except Exception as e:
        print(f"Error setting up tracking: {e}")
        return False

def get_all_tracked_products() -> list:
    """Retrieves all tracking rules along with their product details."""
    db = get_db()
    if not db: return []
    
    try:
        data, count = db.table("tracking").select("*, products(*)").execute()
        return data[1] if hasattr(data, "index") else data[1] # Handle standard response
    except Exception as e:
        print(f"Error fetching tracked products: {e}")
        return []

def get_latest_price(product_id: int) -> float | None:
    """Fetches the last recorded price for a product."""
    db = get_db()
    if not db: return None
    
    try:
        data, count = db.table("price_history").select("price").eq("product_id", product_id).order("timestamp", desc=True).limit(1).execute()
        if len(data[1]) > 0:
            return data[1][0]["price"]
        return None
    except Exception as e:
        print(f"Error fetching latest price: {e}")
        return None
