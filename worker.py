import sys
import os

# Allow running this script directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from workers.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
