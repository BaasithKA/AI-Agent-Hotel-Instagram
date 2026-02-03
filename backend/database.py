import os
import urllib.parse
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine

load_dotenv()


class Hotel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id_hash: str = Field(index=True, unique=True)
    hotel_name: str
    location: str
    discounted_price: Optional[str] = None
    original_price: Optional[str] = None
    rating: Optional[str] = None
    rating_text: Optional[str] = None
    review_count: Optional[str] = None
    review_summary: Optional[str] = None
    amenities: Optional[str] = None
    deal_badge: Optional[str] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    is_processed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SocialPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    hook: str
    caption: str
    hashtags: str
    status: str = Field(default="ready")
    created_at: datetime = Field(default_factory=datetime.utcnow)


db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_DATABASE", "hotel_agent_db")
db_user = os.getenv("DB_USERNAME", "postgres")
db_pass = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", ""))

DATABASE_URL = (
    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
