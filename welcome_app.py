# welcome_app.py — Telegram "welcome" bot via webhook (Railway-ready)

from telebot import TeleBot, types
from flask import Flask, request, abort
import os
import html  # NEW

# --- ENV ---
BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")   # set in Railway Variables
RAILWAY_URL = os.getenv("RAILWAY_URL")          # e.g. https://your-app.up.railway.app
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is not set!")

# Use HTML parse mode for safer mentions (no Markdown escaping headaches)
bot = TeleBot(BOT_TOKEN, parse_mode="HTML")

app = Flask(__name__)


# Put this near the top of welcome_app.py
SECTION_LINKS = {
    # REPLACE these with the links you copied from Telegram
    "info":       "https://t.me/c/3056610802/7/1",
    "rules":      "https://t.me/c/3056610802/13/1",
    "reviews":    "https://t.me/c/3056610802/3/1",
    "giveaways":  "https://t.me/c/3056610802/2/1",
    "announce":   "https://t.me/c/3056610802/9/1",
}


# --- Utility: internal "t.me/c" id from chat_id ---
def internal_chat_id(chat_id: int) -> str:
    """
    For supergroups/channels, t.me/c/<internal>/<msg_id> uses chat_id without the '-100' prefix.
    Example: chat_id = -1003056610802 -> internal '3056610802'
    """
    s = str(chat_id)
    return s[4:] if s.startswith("-100") else s.lstrip("-")

# NEW: prefer public @username link if available; fall back to t.me/c/…
def chat_link_base(chat):
    if getattr(chat, "username", None):
        return f"https://t.me/{chat.username}"
    return f"https://t.me/c/{internal_chat_id(chat.id)}"

# Global variable to store pinned message ID
PINNED_MSG_ID = None

# --- WELCOME HANDLER ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    global PINNED_MSG_ID

    # Collect all new members' names
    new_names = []
    for new_member in message.new_chat_members:
        display_name = (new_member.first_name or "there").strip()
        mention = f'<a href="tg://user?id={new_member.id}">{html.escape(display_name)}</a>'
        new_names.append(mention)


    joined_text = ", ".join(new_names)

    welcome_text = (
        f"✨ Welcome to Golden Fork, {joined_text}! ✨\n"
        f"The place where every reservation means £50 in savings.\n\n"
        f"👉 To get started, pick an option below:"
    )

    # Compute base link prefix for this chat (public link if exists, else t.me/c)
    base = chat_link_base(message.chat)  # NEW

    # Inline buttons for main topics (replace message IDs with yours)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ℹ️ Service Info", url=SECTION_LINKS["info"]),
        types.InlineKeyboardButton("❗ Rules",         url=SECTION_LINKS["rules"])
    )
    markup.add(
        types.InlineKeyboardButton("⭐ Reviews",       url=SECTION_LINKS["reviews"]),
        types.InlineKeyboardButton("🎁 Giveaways",    url=SECTION_LINKS["giveaways"])
    )
    markup.add(
        types.InlineKeyboardButton("📢 Announcements", url=SECTION_LINKS["announce"])
    )
    markup.add(
        # Deep link so mobile opens your bot and starts the flow cleanly
        types.InlineKeyboardButton("🍴 Place your order – Reserve with £50 off",
                                url="https://t.me/axel_fork_bot?start=reserve")
    )

    kwargs = {}
    if getattr(message, "message_thread_id", None):
        kwargs["message_thread_id"] = message.message_thread_id

    # If we don't have a pinned message yet → create one
    if PINNED_MSG_ID is None:
        sent = bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=markup,
            disable_web_page_preview=True,
            disable_notification=True,
            **kwargs
        )
        PINNED_MSG_ID = sent.message_id
        bot.pin_chat_message(message.chat.id, PINNED_MSG_ID, disable_notification=True)
    else:
        # Edit the existing pinned message
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=PINNED_MSG_ID,
                text=welcome_text,
                reply_markup=markup,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"⚠️ Could not edit pinned message: {e}")

# --- Flask / webhook plumbing ---
@app.get("/health")
def health():
    return "ok", 200

@app.post(f"/webhook/{BOT_TOKEN}")
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        update = types.Update.de_json(request.get_data(as_text=True))
        bot.process_new_updates([update])
        return "OK", 200
    abort(403)

if __name__ == "__main__":
    if not RAILWAY_URL:
        raise ValueError("❌ RAILWAY_URL is not set! (e.g., https://your-app.up.railway.app)")

    # Reset & set webhook
    bot.remove_webhook()
    bot.set_webhook(
        url=f"{RAILWAY_URL}/webhook/{BOT_TOKEN}",
        drop_pending_updates=True,
        allowed_updates=["message"]
    )

    port = int(os.getenv("PORT", "8080"))
    print(f"🤖 Welcome bot webhook running on port {port}…")
    app.run(host="0.0.0.0", port=port)
