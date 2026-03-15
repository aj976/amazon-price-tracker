# from bs4 import BeautifulSoup
# import requests,smtplib
# # Add the os and dotenv modules
# import os
# from dotenv import load_dotenv
# # Load environment variables from .env file
# load_dotenv()
#
# # url ="https://appbrewery.github.io/instant_pot/"
# # Live Site
# url = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"
# # ====================== Add Headers to the Request ===========================
#
# # Full headers would look something like this
# header = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br, zstd",
#     "Accept-Language": "en-GB,de;q=0.8,fr;q=0.6,en;q=0.4,ja;q=0.2",
#     "Dnt": "1",
#     "Priority": "u=1",
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Sec-Gpc": "1",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
# }
#
# # A minimal header would look like this:
# # header = {
# #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
# #     "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
# # }
# response = requests.get(url=url,headers=header)
# website_html = response.content #or response.text
#
# soup = BeautifulSoup(website_html, "html.parser")
# print(soup.prettify())
#
# # Find the HTML element that contains the price
# # the offscreen class contains all 3 types of prices
# # and the dolal sign(basically the entire text)
# price = soup.find(class_="a-offscreen").get_text()
#
# # Remove the dollar sign using split
# price_without_currency = price.split("$")[1]
#
# # Convert to floating point number
# price_as_float = float(price_without_currency)
# print(price_as_float)
# # ====================== Send an Email ===========================
# title = soup.find(id="productTitle").get_text().strip()
# print(title)
#
# # Set the price below which you would like to get a notification
# BUY_PRICE = 70
#
# if price_as_float < BUY_PRICE:
#     message = f"{title} is on sale for {price}!"
#
#     # ====================== Use environment variables ===========================
#
#     with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
#         connection.starttls()
#         result = connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
#         connection.sendmail(
#             from_addr=os.environ["EMAIL_ADDRESS"],
#             to_addrs=os.environ["EMAIL_ADDRESS"],
#             msg=f"Subject:Amazon Price Alert!\n\n{message}\n{url}".encode("utf-8")
#         )

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