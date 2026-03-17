import sys
import os

# Allow running this script directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import schedule
import logging

from cli.commands import run_cli
from services.tracker import run_tracker_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def start_scheduler():
    """
    Runs the tracking job every 2 hours continuously.
    """
    logging.info("Starting background scheduler... (Runs every 2 hours)")
    
    # Run once immediately on startup
    run_tracker_job()
    
    # Schedule every 2 hours
    schedule.every(2).hours.do(run_tracker_job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # Wait 1 minute between checks
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments are passed, route to CLI commands
        if sys.argv[1] == "schedule":
            start_scheduler()
        else:
            run_cli()
    else:
        # Default behavior: Print help if no args provided
        run_cli()