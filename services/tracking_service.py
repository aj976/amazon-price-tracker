import logging
from typing import Dict, Any

from scraper.amazon_scraper import scrape_amazon_product
from database.repository import Repository
from services.notification_service import trigger_alert

logger = logging.getLogger(__name__)

class TrackingService:
    def __init__(self, repository: Repository):
        self.repo = repository

    def track_product(self, url: str, target_price: float) -> Dict[str, Any]:
        """
        Manually tracks a new or existing product.
        Adds it to the DB if missing, sets the tracking target, and does an initial fetch.
        """
        logger.info(f"Setting up tracking for: {url}")
        
        try:
            # 1. Scrape current data
            scrape_result = scrape_amazon_product(url)
            if not scrape_result.get("success") or not scrape_result.get("asin"):
                return {"success": False, "message": "Failed to scrape product details from Amazon."}
                
            asin = scrape_result["asin"]
            title = scrape_result.get("title", "Unknown Product")
            current_price = scrape_result.get("price")
            
            # 2. Add or Get Product from DB
            product = self.repo.insert_or_update_product(asin, title, url)
            product_id = product["id"]
            
            # 3. Store initial price if available
            if current_price is not None:
                self.repo.store_price(product_id, current_price)
            else:
                logger.warning(f"Could not extract current price for {asin} during setup.")
                
            # 4. Setup tracking rule
            tracking_record = self.repo.setup_tracking(product_id, target_price)
            
            return {
                "success": True, 
                "message": f"Successfully tracking '{title}'. Target: ₹{target_price}",
                "data": product
            }
        except Exception as e:
            logger.error(f"Error in tracking setup: {e}")
            return {"success": False, "message": f"An internal error occurred: {str(e)}"}

    def run_tracking_iteration(self):
        """
        Orchestrates scraping all tracked products, updating the prices, and triggering notifications.
        """
        logger.info("Starting scheduled price tracker iteration...")
        
        try:
            tracked_items = self.repo.get_all_tracked_products()
            
            if not tracked_items:
                logger.info("No tracked products found.")
                return
                
            for item in tracked_items:
                product = item.get("products")
                if not product:
                    continue
                    
                product_id = product.get("id")
                title = product.get("title")
                url = product.get("url")
                target_price = item.get("target_price")
                tracking_id = item.get("id")
                
                logger.info(f"Checking price for: {title[:30]}...")
                
                # Fetch current price from Amazon
                scrape_result = scrape_amazon_product(url)
                current_price = scrape_result.get("price")
                
                if not current_price:
                    logger.warning(f"Failed to fetch current price for {title[:30]}")
                    continue
                    
                # Store the new price to history
                self.repo.store_price(product_id, current_price)
                
                # Check for price drop
                last_notified = item.get("last_notified_price")
                
                if current_price <= target_price:
                    if last_notified is None or current_price < last_notified:
                        logger.info(f"🚨 TARGET HIT! {title[:20]} is ₹{current_price} (Target: ₹{target_price})")
                        
                        alert_sent = trigger_alert(title, current_price, target_price, url)
                        if alert_sent:
                            # Update the tracking table to reflect the last notified price
                            self.repo.update_last_notified_price(tracking_id, current_price)
                    else:
                        logger.info(f"Target already hit previously (Current: ₹{current_price}, Last Notified: ₹{last_notified}). Skipping alert.")
                else:
                    logger.info(f"No drop. Current: ₹{current_price}, Target: ₹{target_price}")
                    
            logger.info("Tracking iteration completed.")
        except Exception as e:
            logger.error(f"Error during tracking iteration: {e}")
