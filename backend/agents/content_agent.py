import os
from typing import List, Dict

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()


class InstagramContent(BaseModel):
    hook: str = Field(description="Hook pembuka yang kuat.")
    caption: str = Field(description="Caption Instagram estetik dan persuasif.")
    hashtags: List[str] = Field(description="Hashtag travel viral.")


def _safe(value, fallback=""):
    return value if value else fallback


def generate_hotel_content(hotel_data: Dict):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY tidak ditemukan"}

    client = genai.Client(api_key=api_key)

    prompt = f"""
Kamu adalah social media strategist profesional untuk akun Instagram travel & hotel.

Jika ada data yang kosong atau tidak tersedia,
buat konten yang tetap masuk akal dan menarik TANPA mengarang fakta spesifik.

DATA HOTEL:
Nama Hotel: {_safe(hotel_data.get('hotel_name'), 'Hotel pilihan favorit traveler')}
Lokasi: {_safe(hotel_data.get('location'), 'lokasi strategis')}
Harga Promo: {_safe(hotel_data.get('discounted_price'), 'tersedia promo menarik')}
Harga Normal: {_safe(hotel_data.get('original_price'))}
Rating: {_safe(hotel_data.get('rating'), 'rating tinggi')} ({_safe(hotel_data.get('rating_text'))})
Jumlah Review: {_safe(hotel_data.get('review_count'), 'banyak ulasan positif')}
Ringkasan Review: {_safe(hotel_data.get('review_summary'), 'disukai banyak tamu')}
Badge Promo: {_safe(hotel_data.get('deal_badge'), 'Promo Terbatas')}
Fasilitas: {_safe(", ".join(hotel_data.get('amenities', [])), 'fasilitas lengkap')}
Deskripsi Hotel: {_safe(hotel_data.get('summary'), 'hotel nyaman untuk liburan maupun staycation')}

TUGAS:
1. Buat 1 HOOK yang kuat
2. Buat caption Instagram estetik (2–3 paragraf)
3. Tonality: santai, premium, travel vibes
4. Tekankan value pengalaman menginap
5. Sertakan CTA halus
6. Gunakan emoji secukupnya
7. Tambahkan 8–12 hashtag travel & hotel

ATURAN:
- Jangan menyebut harga numerik
- Jangan menyebut link
- Jangan menyebut tipe kamar
- Output HARUS JSON valid
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": InstagramContent.model_json_schema()
            }
        )

        return InstagramContent.model_validate_json(response.text)

    except Exception as e:
        return {
            "error": "Gagal generate konten",
            "detail": str(e),
            "hotel": hotel_data.get("hotel_name")
        }
