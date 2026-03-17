import argparse
import sys
import logging
from utils.parser import is_valid_amazon_url
from services.tracker import track_product, run_tracker_job
from database import db

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

def handle_add(args):
    """Handles the 'add' CLI command."""
    url = args.url
    target_price = args.price
    
    if not is_valid_amazon_url(url):
        print(f"Error: Invalid Amazon URL provided -> {url}")
        sys.exit(1)
        
    print(f"Adding product to tracker... Target price: ₹{target_price}")
    result = track_product(url, target_price)
    
    if result.get("success"):
        print(f"✅ Success: {result['message']}")
    else:
        print(f"❌ Failed: {result['message']}")

def handle_list(args):
    """Handles the 'list' CLI command."""
    print("\n--- Tracked Products ---")
    items = db.get_all_tracked_products()
    
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

def handle_track_now(args):
    """Handles the 'track-now' CLI command."""
    print("Initiating manual tracking job...")
    run_tracker_job()
    print("Tracking job finished. Check console logs for details.")

def handle_remove(args):
    """Handles the 'remove' CLI command."""
    asin = args.asin
    db_client = db.get_db()
    if not db_client:
        print("Database connection error.")
        return
        
    try:
        # Get product ID first
        product = db.get_product_by_asin(asin)
        if not product:
            print(f"Product with ASIN '{asin}' not found.")
            return
            
        product_id = product["id"]
        
        # We can just delete the tracking row OR delete the whole product which cascades
        result, count = db_client.table("products").delete().eq("id", product_id).execute()
        print(f"✅ Removed product ASIN {asin} from tracking.")
    except Exception as e:
        print(f"❌ Failed to remove product: {e}")

def run_cli():
    """Main CLI routing function."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    if args.command == "add":
        handle_add(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "track-now":
        handle_track_now(args)
    elif args.command == "remove":
        handle_remove(args)
    else:
        parser.print_help()