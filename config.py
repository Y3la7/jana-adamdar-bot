"""
config.py — centralized configuration loader.
All secrets and paths come from the .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Bot credentials ──────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/bot.db")

# ─── Contact details (edit here, no code changes needed) ─────────────────────
CONTACTS = {
    "phone": "+7 700 455 6312",
    "telegram": "@y3la7",
    "instagram": "https://www.instagram.com/y3la7?igsh=ZTN4OG4wMjQ1dWUw&utm_source=qr",
    "email": "elgantileuberdiev@gmail.com",
}

# ─── Validate required settings ───────────────────────────────────────────────
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set in .env file")
