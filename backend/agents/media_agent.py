import os
from typing import Optional

import requests


def download_hotel_image(url: str, hotel_id: str) -> Optional[str]:
    if not url:
        return None

    os.makedirs("output/images", exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; HotelMediaBot/1.0)"
    }

    try:
        r = requests.get(url, headers=headers, timeout=25, stream=True)

        if r.status_code != 200:
            print(f"⚠️ Image download failed [{r.status_code}] for hotel {hotel_id}")
            return None

        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"⚠️ Invalid content-type ({content_type}) for hotel {hotel_id}")
            return None

        ext = content_type.split("/")[-1].split(";")[0]
        if ext not in ["jpeg", "jpg", "png", "webp"]:
            ext = "jpg"

        path = f"output/images/{hotel_id}.{ext}"

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return path

    except requests.exceptions.Timeout:
        print(f"⏱️ Image download timeout for hotel {hotel_id}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Image download error for hotel {hotel_id}: {e}")
        return None
