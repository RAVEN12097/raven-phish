
import os
import logging
import re
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "account",
    "password", "wallet", "update", "free"
]


def scan_url(text):
    match = re.search(r"https?://[^\s]+", text)

    if not match:
        return "لینکی پیدا نشد."

    url = match.group(0).rstrip(".,!?")
    parsed = urlparse(url)
    domain = parsed.hostname or ""

    reasons = []

    if parsed.scheme != "https":
        reasons.append("اتصال HTTPS ندارد")

    if "@" in parsed.netloc:
        reasons.append("دارای علامت @ است")

    if domain.count(".") >= 4:
        reasons.append("تعداد زیردامنه‌ها زیاد است")

    if any(word in url.lower() for word in SUSPICIOUS_WORDS):
        reasons.append("دارای واژه‌های مشکوک است")

    if reasons:
        return "⚠️ لینک مشکوک:\n\n" + "\n".join(
            "• " + reason for reason in reasons
        )

    return "🟡 نشانه مشکوک آشکاری پیدا نشد؛ امنیت لینک تضمین نمی‌شود."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐦‍⬛ RAVEN PHISH\n\nلینک موردنظر را برای بررسی بفرست."
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = scan_url(update.message.text)
    await update.message.reply_text(result)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("RAVEN PHISH is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
      
