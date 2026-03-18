import logging
from database.db import get_db

logger = logging.getLogger(__name__)

class Repository:
    """
    Data Access Layer (Repository) for Supabase operations.
    Abstracts all direct DB interactions so services don't need to import db directly.
    """
    def __init__(self):
        self.db = get_db()
        if not self.db:
            logger.error("Failed to initialize database connection in repository.")
            raise ConnectionError("Database connection unavailable.")

    def insert_or_update_product(self, asin: str, title: str, url: str) -> dict:
        """Inserts a new product or ignores if ASIN already exists."""
        try:
            data, count = self.db.table("products").upsert(
                {"asin": asin, "title": title, "url": url}, 
                on_conflict="asin"
            ).execute()
            
            if data and data[1]:
                return data[1][0]
            else:
                 raise Exception("Failed to retrieve upserted product data.")
        except Exception as e:
            logger.error(f"Error inserting product {asin}: {e}")
            raise

    def get_product_by_asin(self, asin: str) -> dict | None:
        try:
            data, count = self.db.table("products").select("*").eq("asin", asin).execute()
            if data and data[1]:
                return data[1][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching product {asin}: {e}")
            raise

    def get_all_tracked_products(self) -> list:
        """Retrieves all tracking rules along with their product details and latest price."""
        try:
            data, count = self.db.table("tracking").select("*, products(*)").execute()
            items = data[1] if hasattr(data, "index") else data[1]
            
            # Decorate the products with their most recent scraped price
            for item in items:
                try:
                    product_id = item["product_id"]
                    ph_data, _ = self.db.table("price_history").select("price").eq("product_id", product_id).order("timestamp", desc=True).limit(1).execute()
                    if ph_data[1] and "products" in item and isinstance(item["products"], dict):
                        item["products"]["latest_price"] = ph_data[1][0]["price"]
                except Exception as e:
                    logger.error(f"Error fetching latest price for product {item.get('product_id')}: {e}")
            
            return items
        except Exception as e:
            logger.error(f"Error fetching tracked products: {e}")
            raise

    def store_price(self, product_id: int, price: float) -> bool:
        """Records a new price for the given product ID."""
        try:
            self.db.table("price_history").insert(
                {"product_id": product_id, "price": price}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error storing price for product {product_id}: {e}")
            raise

    def get_latest_price(self, product_id: int) -> float | None:
        """Fetches the last recorded price for a product."""
        try:
            data, count = self.db.table("price_history").select("price").eq("product_id", product_id).order("timestamp", desc=True).limit(1).execute()
            if data[1]:
                return data[1][0]["price"]
            return None
        except Exception as e:
            logger.error(f"Error fetching latest price for {product_id}: {e}")
            raise

    def setup_tracking(self, product_id: int, target_price: float) -> dict:
        """Sets up or updates the target tracking price for a product."""
        try:
            response, count = self.db.table("tracking").select("*").eq("product_id", product_id).execute()
            if response[1]:
                res, _ = self.db.table("tracking").update({"target_price": target_price}).eq("product_id", product_id).execute()
                return res[1][0]
            else:
                res, _ = self.db.table("tracking").insert({"product_id": product_id, "target_price": target_price}).execute()
                return res[1][0]
        except Exception as e:
            logger.error(f"Error configuring tracking for {product_id}: {e}")
            raise
            
    def update_last_notified_price(self, tracking_id: int, price: float):
        """Updates the last price a user was notified about."""
        try:
             self.db.table("tracking").update({"last_notified_price": price}).eq("id", tracking_id).execute()
        except Exception as e:
            logger.error(f"Error updating notified price for tracking item {tracking_id}: {e}")
            raise

    def delete_product(self, asin: str):
        """Removes a tracked product."""
        try:
             product = self.get_product_by_asin(asin)
             if not product:
                 raise ValueError("Product not found.")
             self.db.table("products").delete().eq("id", product["id"]).execute()
        except Exception as e:
            logger.error(f"Error deleting product {asin}: {e}")
            raise
