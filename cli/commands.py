import argparse
import sys
import logging
from utils.parser import is_valid_amazon_url
from database.repository import Repository
from services.tracking_service import TrackingService

def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Amazon Price Tracker (APT)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add a new product to track")
    add_parser.add_argument("url", type=str, help="Amazon product URL")
    add_parser.add_argument("price", type=float, help="Target price to trigger alert")
    
    # 'list' command
    subparsers.add_parser("list", help="List all tracked products")
    
    # 'track-now' command
    subparsers.add_parser("track-now", help="Manually run the tracking job immediately")
    
    # 'remove' command
    remove_parser = subparsers.add_parser("remove", help="Remove a tracked product")
    remove_parser.add_argument("asin", type=str, help="The ASIN of the product to remove")
    
    return parser

def handle_add(args, tracking_service: TrackingService):
    """Handles the 'add' CLI command."""
    url = args.url
    target_price = args.price
    
    if not is_valid_amazon_url(url):
        print(f"Error: Invalid Amazon URL provided -> {url}")
        sys.exit(1)
        
    print(f"Adding product to tracker... Target price: ₹{target_price}")
    result = tracking_service.track_product(url, target_price)
    
    if result.get("success"):
        print(f"✅ Success: {result['message']}")
    else:
        print(f"❌ Failed: {result['message']}")

def handle_list(args, repo: Repository):
    """Handles the 'list' CLI command."""
    print("\n--- Tracked Products ---")
    try:
        items = repo.get_all_tracked_products()
        if not items:
            print("No products currently tracked.")
            return
            
        for item in items:
            product = item.get("products")
            if not product: continue
            
            asin = product.get("asin")
            title = product.get("title", "")[:40]
            target = item.get("target_price")
            notified = item.get("last_notified_price", "N/A")
            
            print(f"• ASIN: {asin} | Target: ₹{target} | (Last Notified: ₹{notified})")
            print(f"  Title: {title}...")
    except Exception as e:
        print(f"❌ Failed to fetch list: {e}")

def handle_track_now(args, tracking_service: TrackingService):
    """Handles the 'track-now' CLI command."""
    print("Initiating manual tracking job...")
    tracking_service.run_tracking_iteration()
    print("Tracking job finished. Check console logs for details.")

def handle_remove(args, repo: Repository):
    """Handles the 'remove' CLI command."""
    asin = args.asin
    try:
        repo.delete_product(asin)
        print(f"✅ Removed product ASIN {asin} from tracking.")
    except Exception as e:
        print(f"❌ Failed to remove product: {e}")

def run_cli():
    """Main CLI routing function."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    repo = Repository()
    tracking_service = TrackingService(repo)
    
    if args.command == "add":
        handle_add(args, tracking_service)
    elif args.command == "list":
        handle_list(args, repo)
    elif args.command == "track-now":
        handle_track_now(args, tracking_service)
    elif args.command == "remove":
        handle_remove(args, repo)
    else:
        parser.print_help()