import time
import schedule
import logging
from database.repository import Repository
from services.tracking_service import TrackingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def start_scheduler():
    """
    Runs the tracking job every 2 hours continuously.
    """
    logging.info("Starting background scheduler... (Runs every 2 hours)")
    
    try:
        repo = Repository()
        tracking_service = TrackingService(repo)
    except Exception as e:
        logging.error(f"Failed to initialize services for scheduler: {e}")
        return
    
    # Run once immediately on startup
    tracking_service.run_tracking_iteration()
    
    # Schedule every 2 hours
    schedule.every(2).hours.do(tracking_service.run_tracking_iteration)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # Wait 1 minute between checks
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")
