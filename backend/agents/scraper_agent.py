import os
from typing import List, Optional

from dotenv import load_dotenv
from firecrawl import Firecrawl
from pydantic import BaseModel, Field

load_dotenv()


class HotelItem(BaseModel):
    hotel_name: Optional[str] = Field(None, description="Nama lengkap hotel.")
    location: Optional[str] = Field(None, description="Area atau alamat hotel.")
    discounted_price: Optional[str] = Field(None, description="Harga promo saat ini.")
    original_price: Optional[str] = Field(None, description="Harga asli sebelum diskon.")
    rating: Optional[str] = Field(None, description="Rating hotel (angka + label).")
    rating_text: Optional[str] = Field(None, description="Label kualitas rating.")
    review_count: Optional[str] = Field(None, description="Jumlah ulasan pengguna.")
    review_summary: Optional[str] = Field(None, description="Ringkasan sentimen ulasan.")
    amenities: List[str] = Field(default_factory=list, description="Fasilitas utama hotel.")
    deal_badge: Optional[str] = Field(None, description="Label promo.")
    image_url: Optional[str] = Field(None, description="URL gambar utama hotel.")
    summary: Optional[str] = Field(None, description="Deskripsi hotel.")


class HotelList(BaseModel):
    hotels: List[HotelItem]


def scrape_hotels(url: str):
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return {"error": "FIRECRAWL_API_KEY tidak ditemukan"}

    app = Firecrawl(api_key=api_key)

    try:
        print(f"🕵️ Menjalankan scraper pada: {url}")

        result = app.scrape(
            url=url,
            formats=[
                {
                    "type": "json",
                    "schema": HotelList.model_json_schema(),
                    "prompt": (
                        "Extract hotel listings shown as hotel cards on the page. "
                        "Each hotel should represent one visible hotel result. "
                        "If a field is not visible, return null. Do not hallucinate."
                    )
                }
            ],
            only_main_content=False,
            actions=[
                {"type": "wait", "milliseconds": 5000},
                {"type": "scroll", "direction": "down", "amount": 1200},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "down", "amount": 1200},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "down", "amount": 1200},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "down", "amount": 1200},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "up", "amount": 600},
                {"type": "wait", "milliseconds": 2000},
            ],
            wait_for=60000
        )

        if not result:
            return []

        data_json = result.get("json") if isinstance(result, dict) else getattr(result, "json", None)
        hotels = data_json.get("hotels", []) if data_json else []

        print(f"✅ Hotel terscrape: {len(hotels)}")

        return hotels

    except Exception as e:
        return {"error": str(e)}
