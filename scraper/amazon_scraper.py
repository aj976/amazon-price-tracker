import sys
import os

# Allow running this script directly by adding the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests 
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

from utils.parser import extract_asin

class AmazonScraper:
    def __init__(self):
        # Specific headers to bypass basic bot protection
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.max_retries = 3
        self.retry_delay = 2 # seconds

    def _clean_price(self, price_str: str) -> Optional[float]:
        """
        Cleans the price string and converts it to a float.
        """
        if not price_str:
            return None
        
        # Remove currency symbols and commas
        cleaned = "".join(c for c in price_str if c.isdigit() or c == '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return None

    def fetch_product(self, url: str) -> Dict[str, Any]:
        """
        Fetches the product title and price from the given Amazon URL.
        Retries up to `max_retries` times on failure.
        """
        asin = extract_asin(url)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                # Check for blocking (often 503 from Amazon)
                if response.status_code == 503:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract Title
                title_elem = soup.select_one("#productTitle")
                title = title_elem.text.strip() if title_elem else ("Unknown Title" if asin else "Invalid URL")
                
                if not title_elem:
                   # Sometimes Amazon returns a captcha page which we can't parse easily
                   if "captcha" in str(response.content).lower():
                        continue # Retry on captcha
                
                # Extract Price
                price = None
                
                # Multiple Price Selectors
                price_selectors = [
                    ".a-price-whole", 
                    ".a-offscreen", 
                    "#priceblock_ourprice", 
                    "#priceblock_dealprice"
                ]
                
                for selector in price_selectors:
                    price_elem = soup.select_one(selector)
                    if price_elem:
                        # For .a-price-whole, we usually need to combine it with a fraction, but often just the whole number is fine for tracking
                        extracted_price = self._clean_price(price_elem.text)
                        if extracted_price is not None:
                            price = extracted_price
                            break
                
                return {
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "url": url,
                    # Consider it a success if we got the ASIN and a valid title
                    "success": True if asin and title and title != "Invalid URL" else False
                }
                
            except requests.RequestException as e:
                # Log error here in a real application
                if attempt == self.max_retries - 1:
                    break
                time.sleep(self.retry_delay * (attempt + 1))
                
        # If all retries fail or we can't find the price
        return {
            "asin": asin,
            "title": "Failed to fetch title",
            "price": None,
            "url": url,
            "success": False
        }

# Helper function
def scrape_amazon_product(url: str) -> Dict[str, Any]:
    scraper = AmazonScraper()
    return scraper.fetch_product(url)

if __name__ == "__main__":
    import json
    # Use a dummy test URL if none is provided via command line
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.amazon.in/dp/B08N5WRWNW"
    print(f"Testing Scraper on URL: {test_url}")
    result = scrape_amazon_product(test_url)
    print("\nResult:")
    print(json.dumps(result, indent=2))
