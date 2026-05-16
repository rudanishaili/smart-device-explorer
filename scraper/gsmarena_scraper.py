import os
import sys
import time
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

BASE_URL = "https://www.gsmarena.com/"

BRANDS = {
    "Samsung": "https://www.gsmarena.com/samsung-phones-9.php",
    "Apple": "https://www.gsmarena.com/apple-phones-48.php",
    "Xiaomi": "https://www.gsmarena.com/xiaomi-phones-80.php",
    "OnePlus": "https://www.gsmarena.com/oneplus-phones-95.php",
    "Realme": "https://www.gsmarena.com/realme-phones-118.php",
    "Vivo": "https://www.gsmarena.com/vivo-phones-98.php",
    "Oppo": "https://www.gsmarena.com/oppo-phones-82.php",
    "Motorola": "https://www.gsmarena.com/motorola-phones-4.php",
}


def clean_gb_value(value):
    if not value:
        return ""

    value = value.upper().replace(" ", "")

    if "GB" in value:
        return value

    return ""


def get_phone_details(phone_url):
    response = requests.get(phone_url, headers=HEADERS, timeout=15)
    response.raise_for_status()

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

        if not key or not value:
            continue

        key_text = key.get_text(strip=True).lower()
        value_text = value.get_text(" ", strip=True)

        if "size" in key_text and specs["display"] == "":
            specs["display"] = value_text

        elif "chipset" in key_text and specs["processor"] == "":
            specs["processor"] = value_text

        elif "single" in key_text and specs["camera"] == "":
            specs["camera"] = value_text

        elif "internal" in key_text:
            first_variant = value_text.split(",")[0].strip()
            words = first_variant.split()

            gb_values = []

            for word in words:
                if "GB" in word.upper():
                    gb_values.append(clean_gb_value(word))

            if len(gb_values) >= 1:
                specs["storage"] = gb_values[0]

            if len(gb_values) >= 2:
                specs["ram"] = gb_values[1]

        elif "type" in key_text and specs["battery"] == "":
            if "mah" in value_text.lower() or "li-" in value_text.lower():
                specs["battery"] = value_text

    return specs


def generate_price(ram, storage):
    try:
        ram_value = int(ram.replace("GB", "")) if ram else 4
    except:
        ram_value = 4

    try:
        storage_value = int(storage.replace("GB", "")) if storage else 64
    except:
        storage_value = 64

    base_price = 10000

    price = (
        base_price +
        (ram_value * 2500) +
        (storage_value * 120)
    )

    return int(price)


def scrape_phones_by_brand(brand_name, brand_url, limit=5):
    print(f"\nScraping brand: {brand_name}")

    try:
        response = requests.get(brand_url, headers=HEADERS, timeout=15)

        if response.status_code == 429:
            print(f"Too many requests for {brand_name}. Waiting 30 seconds...")
            time.sleep(30)
            return

        response.raise_for_status()

    except Exception as e:
        print(f"Could not open brand page {brand_name}: {e}")
        return

    soup = BeautifulSoup(response.text, "lxml")

    phones = soup.select(".makers li")[:limit]

    print(f"Found {len(phones)} phones for {brand_name}")

    for phone in phones:
        try:
            name_tag = phone.find("span")
            image_tag = phone.find("img")
            link_tag = phone.find("a")

            if not name_tag or not image_tag or not link_tag:
                print("Skipped one phone because required tags were missing")
                continue

            name = name_tag.get_text(strip=True)
            image = image_tag.get("src")
            link = BASE_URL + link_tag.get("href")

            details = get_phone_details(link)

            Device.objects.update_or_create(
                name=name,
                brand=brand_name,
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

            print(f"Saved: {brand_name} - {name}")

            # wait after each phone
            time.sleep(3)

        except Exception as e:
            print(f"Skipped phone because of error: {e}")
            time.sleep(3)


print("Scraper started...")

for brand_name, brand_url in BRANDS.items():
    scrape_phones_by_brand(brand_name, brand_url, limit=5)

    # wait after each brand
    print("Waiting before next brand...")
    time.sleep(10)

print("\nScraping completed.")