import logging
import sys
import os
from typing import Dict, Any

# Allow running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.amazon_scraper import scrape_amazon_product
from database import db
from services.notifier import trigger_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def track_product(url: str, target_price: float) -> Dict[str, Any]:
    """
    Manually tracks a new or existing product. 
    Adds it to the DB if missing, sets the tracking target, and does an initial fetch.
    """
    logging.info(f"Setting up tracking for: {url}")
    
    # 1. Scrape current data to get ASIN and Title
    scrape_result = scrape_amazon_product(url)
    if not scrape_result.get("success") or not scrape_result.get("asin"):
        logging.error("Failed to scrape product. Ensure URL is valid.")
        return {"success": False, "message": "Failed to scrape product details from Amazon."}
        
    asin = scrape_result["asin"]
    title = scrape_result["title"]
    current_price = scrape_result["price"]
    
    # 2. Add or Get Product from DB
    product = db.insert_product(asin, title, url)
    if not product:
        # Fallback if product already existed and wasn't returned by upsert
        product = db.get_product_by_asin(asin)
        
    if not product:
        return {"success": False, "message": "Failed to store product in database."}
        
    product_id = product["id"]
    
    # 3. Store initial price if available
    if current_price is not None:
        db.store_price(product_id, current_price)
    else:
        logging.warning(f"Could not extract current price for {asin} during setup.")
        
    # 4. Setup tracking rule
    success = db.setup_tracking(product_id, target_price)
    
    if success:
        return {
            "success": True, 
            "message": f"Successfully tracking '{title}'. Target: ₹{target_price}",
            "data": product
        }
    return {"success": False, "message": "Failed to setup tracking rule in database."}

def run_tracker_job():
    """
    To be run by a scheduler. Iterates over all tracked products, fetches the latest price,
    compares it with the target price, and triggers an alert if the condition is met.
    """
    logging.info("Starting scheduled price tracker job...")
    
    tracked_items = db.get_all_tracked_products()
    
    if not tracked_items:
        logging.info("No tracked products found.")
        return
        
    for item in tracked_items:
        product = item.get("products")
        if not product:
            continue
            
        product_id = product.get("id")
        title = product.get("title")
        url = product.get("url")
        target_price = item.get("target_price")
        
        logging.info(f"Checking price for: {title[:30]}...")
        
        # 1. Fetch current price from Amazon
        scrape_result = scrape_amazon_product(url)
        current_price = scrape_result.get("price")
        
        if not current_price:
            logging.warning(f"Failed to fetch current price for {title[:30]}")
            continue
            
        # 2. Store the new price to history
        db.store_price(product_id, current_price)
        
        # 3. Check for price drop
        last_notified = item.get("last_notified_price")
        
        # We trigger an alert if:
        # 1) Current price <= Target Price AND
        # 2) We haven't notified about this drop already (e.g., last_notified is None or higher than current)
        
        if current_price <= target_price:
            if last_notified is None or current_price < last_notified:
                logging.info(f"🚨 TARGET HIT! {title[:20]} is ₹{current_price} (Target: ₹{target_price})")
                
                # Send the alert
                alert_sent = trigger_alert(title, current_price, target_price, url)
                
                if alert_sent:
                    # Update the tracking table to reflect the last notified price
                    # To do this safely, we update the tracking record
                    db_client = db.get_db()
                    if db_client:
                        db_client.table("tracking").update(
                            {"last_notified_price": current_price}
                        ).eq("product_id", product_id).execute()
            else:
                logging.info(f"Target already hit previously (Current: ₹{current_price}, Last Notified: ₹{last_notified}). Skipping alert.")
        else:
            logging.info(f"No drop. Current: ₹{current_price}, Target: ₹{target_price}")
            
    logging.info("Job completed.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running Tracker Job Manually...")
        run_tracker_job()
    else:
        print("Run `python services/tracker.py --test` to trigger manual tracker job.")
