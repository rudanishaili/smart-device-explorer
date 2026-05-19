import os
import sys
import django
import pandas as pd
import re

# DJANGO SETUP
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from devices.models import Device


# LOAD CSV
df = pd.read_csv("scraper/laptop_dataset.csv")


def clean_price(price):

    price = str(price)

    # REMOVE NON-NUMBERS
    price = re.sub(r"[^\d]", "", price)

    if price == "":
        return 0

    return int(price)


def get_local_image(name):

    name = str(name).lower()

    if "macbook air" in name:
        return "/media/laptops/macbook_air.png"

    elif "macbook pro" in name:
        return "/media/laptops/macbook_pro.png"

    elif "victus" in name:
        return "/media/laptops/hp_victus.png"

    elif "omen" in name:
        return "/media/laptops/hp_omen.png"

    elif "legion" in name:
        return "/media/laptops/lenovo_legion.png"

    elif "thinkpad" in name:
        return "/media/laptops/thinkpad.png"

    elif "ideapad" in name:
        return "/media/laptops/ideapad.png"

    elif "alienware" in name:
        return "/media/laptops/alienware.png"

    elif "xps" in name:
        return "/media/laptops/dell_xps.png"

    elif "inspiron" in name:
        return "/media/laptops/inspiron.png"

    elif "rog" in name:
        return "/media/laptops/asus_rog.png"

    elif "tuf" in name:
        return "/media/laptops/asus_tuf.png"

    elif "vivobook" in name:
        return "/media/laptops/vivobook.png"

    elif "nitro" in name:
        return "/media/laptops/acer_nitro.png"

    elif "predator" in name:
        return "/media/laptops/predator.png"

    else:
        return "/media/laptops/vivobook.png"


for index, row in df.iterrows():

    try:

        name = str(row.get("Model", "")).strip()

        if not name or name == "nan":
            continue

        brand = name.split()[0]

        price = clean_price(row.get("Price", 0))

        ram = str(row.get("Ram", "")).replace("â€Ž", "").strip()

        storage = str(row.get("SSD", "")).replace("â€Ž", "").strip()

        processor = (
            str(row.get("Generation", "")) + " " +
            str(row.get("Core", ""))
        ).strip()

        display = str(row.get("Display", "")).replace("â€Ž", "").strip()

        graphics = str(row.get("Graphics", "")).strip()

        os_name = str(row.get("OS", "")).strip()

        warranty = str(row.get("Warranty", "")).strip()

        # AMAZON SEARCH LINK
        source_url = (
            "https://www.amazon.in/s?k=" +
            name.replace(" ", "+")
        )

        # PLACEHOLDER IMAGE
        image_url = get_local_image(name)

        Device.objects.update_or_create(

            name=name,

            defaults={

                "category": "laptop",

                "brand": brand,

                "price": price,

                "ram": ram,

                "storage": storage,

                "processor": processor,

                "display": display,

                "battery": warranty,

                "camera": graphics,

                "image_url": image_url,

                "source_url": source_url,
            }
        )

        print(f"Added: {name}")

    except Exception as e:

        print(f"Error on row {index}: {e}")

print("Laptop import completed.")