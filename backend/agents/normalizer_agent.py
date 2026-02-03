import hashlib
from typing import Dict, List


def generate_hotel_id(hotel: Dict) -> str:
    name = (hotel.get("hotel_name") or "").strip().lower()
    loc = (hotel.get("location") or "").strip().lower()
    price = (hotel.get("discounted_price") or "").strip()

    raw = f"{name}|{loc}|{price}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def _clean_str(val, default=None):
    if not val:
        return default
    val = str(val).strip()
    return val if val else default


def _clean_list(val):
    if not isinstance(val, list):
        return []
    return list({v.strip() for v in val if isinstance(v, str) and v.strip()})


def normalize_hotels(hotels: List) -> List[Dict]:
    normalized = []

    if not isinstance(hotels, list) or not hotels:
        return []

    for hotel in hotels:
        if not isinstance(hotel, dict):
            continue

        hotel_name = _clean_str(hotel.get("hotel_name"))
        location = _clean_str(hotel.get("location"))

        if not hotel_name or not location:
            continue

        hotel_id = generate_hotel_id(hotel)

        normalized.append({
            "hotel_id": hotel_id,
            "hotel_name": hotel_name,
            "location": location,
            "discounted_price": _clean_str(hotel.get("discounted_price")),
            "original_price": _clean_str(hotel.get("original_price")),
            "rating": _clean_str(hotel.get("rating")),
            "rating_text": _clean_str(hotel.get("rating_text")),
            "review_count": _clean_str(hotel.get("review_count")),
            "review_summary": _clean_str(hotel.get("review_summary")),
            "amenities": _clean_list(hotel.get("amenities")),
            "deal_badge": _clean_str(hotel.get("deal_badge")),
            "image_url": _clean_str(hotel.get("image_url")),
            "summary": _clean_str(hotel.get("summary")),
        })

    return normalized
