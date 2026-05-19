import os
import sys
import time
import re
import django
import requests

from bs4 import BeautifulSoup


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from devices.models import Device


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_image_from_bing(query):
    search_url = "https://www.bing.com/images/search"

    params = {
        "q": query,
        "form": "HDRSC2",
        "first": "1"
    }

    response = requests.get(
        search_url,
        params=params,
        headers=HEADERS,
        timeout=15
    )

    soup = BeautifulSoup(response.text, "lxml")

    image_tags = soup.find_all("a", class_="iusc")

    for tag in image_tags:
        metadata = tag.get("m")

        if not metadata:
            continue

        match = re.search(r'"murl":"(.*?)"', metadata)

        if match:
            image_url = match.group(1)

            if image_url.startswith("http"):
                return image_url

    return None


laptops = Device.objects.filter(category="laptop")

print(f"Found {laptops.count()} laptops")

for laptop in laptops:

    try:
        query = f"{laptop.name} laptop product image"

        print(f"Searching image for: {laptop.name}")

        image_url = get_image_from_bing(query)

        if image_url:
            laptop.image_url = image_url
            laptop.save()

            print(f"Updated image: {laptop.name}")

        else:
            print(f"No image found for: {laptop.name}")

        time.sleep(3)

    except Exception as e:
        print(f"Error for {laptop.name}: {e}")
        time.sleep(3)

print("Laptop image scraping completed.")