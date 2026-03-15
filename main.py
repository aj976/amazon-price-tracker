from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://www.amazon.com/dp/B075CYMYK6"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# -------- Get Price --------
price_tag = soup.select_one(".a-price .a-offscreen")

if not price_tag:
    raise Exception("Price not found. Amazon likely blocked the request.")

price_text = price_tag.get_text().strip()
price_as_float = float(price_text.replace("INR", "").replace(",", ""))

print("Price:", price_as_float)

# -------- Get Title --------
title_tag = soup.find(id="productTitle")

if not title_tag:
    raise Exception("Title not found")

title = title_tag.get_text().strip()
print("Title:", title)

# -------- Price Alert --------
BUY_PRICE = 100000

if price_as_float < BUY_PRICE:

    message = f"""Subject: Amazon Price Alert!{title} Price dropped to {price_text} {url} """
    print(message)

    with smtplib.SMTP(os.environ["SMTP_ADDRESS"], 587) as connection:
        connection.starttls()

        connection.login(
            os.environ["EMAIL_ADDRESS"],
            os.environ["EMAIL_PASSWORD"]
        )

        connection.sendmail(
            from_addr=os.environ["EMAIL_ADDRESS"],
            to_addrs=os.environ["EMAIL_ADDRESS"],
            msg=message.encode("utf-8")
        )

    print("Email sent.")