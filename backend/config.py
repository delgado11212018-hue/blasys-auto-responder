
import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    APP_ENV = os.getenv("APP_ENV", "development")
    RESPONSE_DELAY_SECONDS = int(os.getenv("RESPONSE_DELAY_SECONDS", "300"))
    AUTO_SEND_POSITIVE = os.getenv("AUTO_SEND_POSITIVE", "true").lower() == "true"
    AUTO_SEND_QUESTIONS = os.getenv("AUTO_SEND_QUESTIONS", "true").lower() == "true"
    AUTO_SEND_NEGATIVE = os.getenv("AUTO_SEND_NEGATIVE", "false").lower() == "true"
    BRAND_NAME = os.getenv("BRAND_NAME", "Your Brand")
    BRAND_TONE = os.getenv("BRAND_TONE", "friendly professional")
    PRIMARY_LANG = os.getenv("PRIMARY_LANG", "es")
    SECONDARY_LANG = os.getenv("SECONDARY_LANG", "en")
    INFLUENCER_USERNAMES = [s.strip().lower() for s in os.getenv("INFLUENCER_USERNAMES", "").split(",") if s.strip()]
    REPEAT_CUSTOMER_NAMES = [s.strip().lower() for s in os.getenv("REPEAT_CUSTOMER_NAMES", "").split(",") if s.strip()]
    FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
    FACEBOOK_VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "")
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    HUBSPOT_PRIVATE_APP_TOKEN = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
