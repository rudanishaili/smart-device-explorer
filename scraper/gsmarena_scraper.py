import os
import sys
import django
import requests
from bs4 import BeautifulSoup


# ADD PROJECT ROOT PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# DJANGO SETUP
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from devices.models import Device


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_phone_details(phone_url):
    response = requests.get(phone_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "lxml")

    specs = {
        "display": "",
        "processor": "",
        "battery": "",
        "camera": "",
        "ram": "",
        "storage": "",
    }

    rows = soup.select("tr")

    for row in rows:
        key = row.find("td", class_="ttl")
        value = row.find("td", class_="nfo")

        if key and value:
            key_text = key.get_text(strip=True).lower()
            value_text = value.get_text(" ", strip=True)

            if "size" in key_text and specs["display"] == "":
                specs["display"] = value_text

            elif "chipset" in key_text:
                specs["processor"] = value_text

            elif "type" in key_text and "battery" in row.get_text(strip=True).lower():
                specs["battery"] = value_text

            elif "single" in key_text and specs["camera"] == "":
                specs["camera"] = value_text

            elif "internal" in key_text:
                first_variant = value_text.split(",")[0].strip()

                words = first_variant.split()

                if len(words) >= 2:
                    specs["storage"] = words[0]
                    specs["ram"] = words[1]

    return specs


def generate_price(ram, storage):

    ram_value = int(ram.replace("GB", "")) if ram else 4
    storage_value = int(storage.replace("GB", "")) if storage else 64

    base_price = 10000

    price = (
        base_price +
        (ram_value * 2500) +
        (storage_value * 120)
    )

    return price

def scrape_samsung_phones(limit=10):
    url = "https://www.gsmarena.com/samsung-phones-9.php"

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "lxml")

    phones = soup.select(".makers li")[:limit]

    for phone in phones:
        name = phone.find("span").text
        image = phone.find("img")["src"]
        link = "https://www.gsmarena.com/" + phone.find("a")["href"]

        details = get_phone_details(link)

        Device.objects.update_or_create(
            name=name,
            brand="Samsung",
            defaults={
                "price": generate_price(details["ram"], details["storage"]),
                "image_url": image,
                "source_url": link,
                "display": details["display"],
                "processor": details["processor"],
                "battery": details["battery"],
                "camera": details["camera"],
                "ram": details["ram"],
                "storage": details["storage"],
            }
        )

        print(f"{name} saved with details")


scrape_samsung_phones(limit=10)