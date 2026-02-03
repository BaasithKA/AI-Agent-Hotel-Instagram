import os
import random
import requests
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from sqlmodel import Session, select

from database import engine, Hotel, SocialPost
from utils import generate_expedia_url
from agents.scraper_agent import scrape_hotels
from agents.normalizer_agent import normalize_hotels
from agents.content_agent import generate_hotel_content

load_dotenv()

scheduler = BackgroundScheduler()
JOB_ID = "robot_pekerja"
bot_logs = []


def add_log(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    bot_logs.insert(0, log_entry)
    if len(bot_logs) > 50:
        bot_logs.pop()


def get_logs():
    return bot_logs


def run_bot_task():
    add_log("🤖 [ROBOT] Memulai siklus kerja...")

    with Session(engine) as session:
        locations = [
            "Bali",
            "Jakarta",
            "Bandung",
            "Yogyakarta",
            "Surabaya",
            "Semarang",
            "Malang",
        ]
        target_loc = random.choice(locations)
        add_log(f"🔎 [ROBOT] Scraping data di: {target_loc}...")

        try:
            url = generate_expedia_url(target_loc)
            raw_data = scrape_hotels(url)

            if not isinstance(raw_data, list):
                raw_data = []

            data = normalize_hotels(raw_data)

            if data:
                saved = 0
                for item in data:
                    id_val = item.get("hotel_id") or item.get("hotel_id_hash")
                    existing = session.exec(
                        select(Hotel).where(Hotel.hotel_id_hash == id_val)
                    ).first()

                    if not existing:
                        hotel = Hotel(
                            hotel_id_hash=id_val,
                            hotel_name=item["hotel_name"],
                            location=item["location"],
                            discounted_price=item["discounted_price"],
                            original_price=item["original_price"],
                            rating=item["rating"],
                            rating_text=item.get("rating_text"),
                            review_count=item.get("review_count"),
                            review_summary=item.get("review_summary"),
                            amenities=", ".join(item["amenities"])
                            if isinstance(item["amenities"], list)
                            else "",
                            deal_badge=item.get("deal_badge"),
                            image_url=item["image_url"],
                            summary=item.get("summary"),
                        )
                        session.add(hotel)
                        saved += 1

                session.commit()

                if saved > 0:
                    add_log(f"✅ [ROBOT] Berhasil simpan {saved} hotel baru.")
                else:
                    add_log(f"ℹ️ [ROBOT] Data {target_loc} sudah up-to-date.")
            else:
                add_log(f"⚠️ [ROBOT] Scraper kosong di {target_loc}.")

        except Exception as e:
            add_log(f"❌ [ROBOT] Error Scrape: {str(e)}")

        hotels = session.exec(
            select(Hotel).where(Hotel.is_processed == False).limit(1)
        ).all()

        for h in hotels:
            try:
                add_log(f"🧠 [ROBOT] Bikin caption untuk: {h.hotel_name}...")
                hotel_data = h.model_dump()
                hotel_data["amenities"] = h.amenities.split(", ") if h.amenities else []

                content = generate_hotel_content(hotel_data)

                if isinstance(content, str) and content.startswith("ERROR"):
                    add_log(f"❌ [ROBOT] Gagal Generate: {content}")

                elif content and hasattr(content, "caption"):
                    hashtags = (
                        ", ".join(content.hashtags)
                        if isinstance(content.hashtags, list)
                        else str(content.hashtags)
                    )
                    post = SocialPost(
                        hotel_id=h.id,
                        hook=content.hook,
                        caption=content.caption,
                        hashtags=hashtags,
                    )
                    session.add(post)
                    h.is_processed = True
                    session.add(h)
                    add_log("✅ [ROBOT] Konten AI selesai dibuat.")
                else:
                    add_log("⚠️ [ROBOT] Gagal generate (Format AI salah).")

            except Exception as e:
                add_log(f"❌ [ROBOT] Error Gen: {str(e)}")

        session.commit()

        post_to_publish = session.exec(
            select(SocialPost, Hotel)
            .join(Hotel)
            .where(SocialPost.status == "ready")
            .limit(1)
        ).first()

        if post_to_publish:
            post, hotel = post_to_publish
            webhook_url = os.getenv("MAKE_WEBHOOK_URL")

            if webhook_url:
                add_log(f"📤 [ROBOT] Uploading {hotel.hotel_name} ke IG...")

                payload = {
                    "hotel_name": hotel.hotel_name,
                    "image_url": hotel.image_url,
                    "caption": f"{post.hook}\n\n{post.caption}\n\n{post.hashtags}",
                    "location": hotel.location,
                    "price": hotel.discounted_price,
                }

                try:
                    res = requests.post(webhook_url, json=payload, timeout=30)

                    if res.status_code == 200:
                        post.status = "published"
                        session.add(post)
                        session.commit()
                        add_log("✅ [ROBOT] SUKSES! Postingan Terbit.")
                    else:
                        add_log(f"❌ [ROBOT] Gagal Upload (Make.com): {res.text}")

                except Exception as e:
                    add_log(f"❌ [ROBOT] Error Koneksi Upload: {str(e)}")
            else:
                add_log("❌ [ROBOT] Webhook URL belum disetting di .env")
        else:
            add_log("ℹ️ [ROBOT] Tidak ada antrian posting.")

    add_log("💤 [ROBOT] Istirahat.")


def init_scheduler():
    try:
        scheduler.start()
        add_log("🚀 System Bot Ready.")
    except Exception:
        pass


def shutdown_scheduler():
    scheduler.shutdown()


def start_bot_job(minutes: int):
    if scheduler.get_job(JOB_ID):
        return False, "Bot sudah berjalan"

    scheduler.add_job(
        run_bot_task,
        "interval",
        minutes=minutes,
        id=JOB_ID,
        misfire_grace_time=300,
        next_run_time=datetime.now(),
    )
    add_log(f"⚙️ Bot START (Interval: {minutes} menit).")
    return True, f"Bot aktif tiap {minutes} menit"


def stop_bot_job():
    if scheduler.get_job(JOB_ID):
        scheduler.remove_job(JOB_ID)
        add_log("🛑 Bot STOP oleh User.")
        return True, "Bot berhasil dimatikan"
    return False, "Bot sedang tidak berjalan"


def check_bot_status():
    return scheduler.get_job(JOB_ID) is not None
