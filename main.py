import requests
from bs4 import BeautifulSoup
import os
import json

# UltraMsg credentials from GitHub Secrets
ULTRA_INSTANCE_ID = os.environ.get("ULTRA_INSTANCE_ID")
ULTRA_TOKEN = os.environ.get("ULTRA_TOKEN")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER")  # e.g. 971501234567

# Bayut search URLs for JLT Cluster D, E, F
URLS = [
    "https://www.bayut.com/to-rent/property/dubai/jumeirah-lake-towers/cluster-d/",
    "https://www.bayut.com/for-sale/property/dubai/jumeirah-lake-towers/cluster-d/",
    "https://www.bayut.com/to-rent/property/dubai/jumeirah-lake-towers/cluster-e/",
    "https://www.bayut.com/for-sale/property/dubai/jumeirah-lake-towers/cluster-e/",
    "https://www.bayut.com/to-rent/property/dubai/jumeirah-lake-towers/cluster-f/",
    "https://www.bayut.com/for-sale/property/dubai/jumeirah-lake-towers/cluster-f/"
]

sent_links = set(json.loads(os.environ.get("SENT_LINKS", "[]")))

def send_whatsapp(message):
    """Send a WhatsApp message via UltraMsg API."""
    url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRA_TOKEN,
        "to": WHATSAPP_NUMBER,
        "body": message
    }
    r = requests.post(url, data=payload)
    print(f"WhatsApp API response: {r.text}")

def scrape_bayut(url):
    """Scrape Bayut listings from a given URL."""
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = []
    for card in soup.select("article"):
        title_tag = card.select_one("h2")
        link_tag = card.select_one("a")
        price_tag = card.select_one("span[class*='amount']")
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = "https://www.bayut.com" + link_tag["href"]
            price = price_tag.get_text(strip=True) if price_tag else "N/A"
            listings.append({
                "title": title,
                "price": price,
                "link": link
            })
    return listings

def main():
    global sent_links
    new_sent_links = set(sent_links)
    for url in URLS:
        listings = scrape_bayut(url)
        for listing in listings:
            if listing["link"] not in sent_links:
                message = f"🏠 {listing['title']}\n💰 {listing['price']}\n🔗 {listing['link']}"
                send_whatsapp(message)
                new_sent_links.add(listing["link"])
    print("::set-output name=SENT_LINKS::" + json.dumps(list(new_sent_links)))

if __name__ == "__main__":
    main()
