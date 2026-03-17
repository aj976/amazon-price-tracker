import re
from urllib.parse import urlparse

def extract_asin(url: str) -> str | None:
    """
    Extracts the 10-character Amazon Standard Identification Number (ASIN) from an Amazon URL.
    Returns the ASIN if found, otherwise None.
    """
    # Regex to capture typical ASIN formats in Amazon URLs
    # Matches /dp/, /product/, /gp/product/, or simply /ASIN/
    match = re.search(r"/(?:dp|product|gp/product|exec/obidos/ASIN)/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    
    # Fallback to checking the end of the URL or other path segment
    match = re.search(r"([A-Z0-9]{10})(?:[/?]|$)", url)
    if match:
        return match.group(1)
        
    return None

def is_valid_amazon_url(url: str) -> bool:
    """
    Checks if the given URL is a valid Amazon URL.
    """
    try:
        parsed = urlparse(url)
        # Check if the domain contains 'amazon'
        if "amazon" not in parsed.netloc.lower():
            return False
        return True
    except Exception:
        return False
