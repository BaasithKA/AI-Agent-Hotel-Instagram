import os
import requests
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select

import bot
from agents.content_agent import generate_hotel_content
from agents.normalizer_agent import normalize_hotels
from agents.scraper_agent import scrape_hotels
from database import Hotel, SocialPost, create_db_and_tables, get_session
from utils import generate_expedia_url

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    bot.init_scheduler()
    yield
    bot.shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/logs")
def get_system_logs():
    return bot.get_logs()


@app.get("/api/bot/status")
def get_bot_status():
    return {"is_running": bot.check_bot_status()}


@app.post("/api/bot/start")
def start_bot(minutes: int = 60):
    success, msg = bot.start_bot_job(minutes)
    if success:
        return {"status": "success", "message": msg}
    return {"status": "already_running", "message": msg}


@app.post("/api/bot/stop")
def stop_bot():
    success, msg = bot.stop_bot_job()
    if success:
        return {"status": "success", "message": msg}
    return {"status": "error", "message": msg}


class ScrapeRequest(BaseModel):
    location: str


@app.post("/api/scrape")
def trigger_scrape(req: ScrapeRequest, session: Session = Depends(get_session)):
    bot.add_log(f"👤 [MANUAL] Scraping {req.location}...")
    url = generate_expedia_url(req.location)
    raw_data = scrape_hotels(url)

    if not isinstance(raw_data, list):
        raw_data = []

    data = normalize_hotels(raw_data)

    if not data:
        bot.add_log("❌ [MANUAL] Scraper gagal.")
        return {"status": "failed", "message": "Scraper gagal mendapatkan data hotel."}

    saved = 0
    for item in data:
        existing = session.exec(
            select(Hotel).where(Hotel.hotel_id_hash == item["hotel_id"])
        ).first()

        if not existing:
            hotel = Hotel(
                hotel_id_hash=item["hotel_id"],
                hotel_name=item["hotel_name"],
                location=item["location"],
                discounted_price=item["discounted_price"],
                original_price=item["original_price"],
                rating=item["rating"],
                rating_text=item["rating_text"],
                review_count=item["review_count"],
                review_summary=item["review_summary"],
                amenities=", ".join(item["amenities"])
                if isinstance(item["amenities"], list)
                else "",
                deal_badge=item["deal_badge"],
                image_url=item["image_url"],
                summary=item["summary"],
            )
            session.add(hotel)
            saved += 1

    session.commit()
    bot.add_log(f"✅ [MANUAL] {saved} hotel baru tersimpan.")
    return {"status": "success", "new_hotels_saved": saved}


@app.post("/api/generate-content")
def trigger_generate(limit: int = 1, session: Session = Depends(get_session)):
    bot.add_log("👤 [MANUAL] Generate Content...")
    hotels = session.exec(
        select(Hotel).where(Hotel.is_processed == False).limit(limit)
    ).all()

    count = 0
    for h in hotels:
        hotel_data = h.model_dump()
        hotel_data["amenities"] = h.amenities.split(", ") if h.amenities else []

        content = generate_hotel_content(hotel_data)

        if not content or not hasattr(content, "caption"):
            continue

        post = SocialPost(
            hotel_id=h.id,
            hook=content.hook,
            caption=content.caption,
            hashtags=", ".join(content.hashtags),
        )

        session.add(post)
        h.is_processed = True
        session.add(h)
        count += 1

    session.commit()
    bot.add_log(f"✅ [MANUAL] {count} konten selesai.")
    return {"status": "success", "generated_count": count}


@app.get("/api/posts")
def get_posts(session: Session = Depends(get_session)):
    results = session.exec(
        select(SocialPost, Hotel)
        .join(Hotel)
        .order_by(SocialPost.id.desc())
    ).all()

    return [
        {
            "post_id": p.id,
            "hotel_name": h.hotel_name,
            "image_url": h.image_url,
            "caption": f"{p.hook}\n\n{p.caption}",
            "hashtags": p.hashtags,
            "status": p.status,
        }
        for p, h in results
    ]


@app.get("/api/hotels/raw")
def get_all_raw_hotels(session: Session = Depends(get_session)):
    return session.exec(select(Hotel).order_by(Hotel.id.desc())).all()


@app.post("/api/posts/{post_id}/publish")
def publish_to_instagram(post_id: int, session: Session = Depends(get_session)):
    result = session.exec(
        select(SocialPost, Hotel)
        .join(Hotel)
        .where(SocialPost.id == post_id)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")

    post, hotel = result
    bot.add_log(f"👤 [MANUAL] Posting {hotel.hotel_name}...")

    webhook_url = os.getenv("MAKE_WEBHOOK_URL")
    if not webhook_url:
        return {"status": "error", "message": "MAKE_WEBHOOK_URL belum disetting"}

    payload = {
        "hotel_name": hotel.hotel_name,
        "image_url": hotel.image_url,
        "caption": f"{post.hook}\n\n{post.caption}\n\n{post.hashtags}",
        "location": hotel.location,
        "price": hotel.discounted_price,
    }

    try:
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            post.status = "published"
            session.add(post)
            session.commit()
            session.refresh(post)
            bot.add_log("✅ [MANUAL] Posting Berhasil!")
            return {"status": "success", "message": "Berhasil dikirim ke Instagram"}

        bot.add_log(f"❌ [MANUAL] Gagal: {response.text}")
        return {"status": "failed", "message": response.text}

    except Exception as e:
        bot.add_log(f"❌ [MANUAL] Error: {str(e)}")
        return {"status": "error", "message": str(e)}
