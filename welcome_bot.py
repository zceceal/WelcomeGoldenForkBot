from telebot import TeleBot, types

# Replace with your bot token from BotFather
BOT_TOKEN = "8471745453:AAGxAXcpp9nT2QanjbiTxg0jnEUU7t9cn9c"

bot = TeleBot(BOT_TOKEN, parse_mode="Markdown")

# --- GREETING HANDLER ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        username = new_member.first_name or "there"

        # Inline buttons for main topics
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("ℹ️ Service Info", url="https://t.me/c/3056610802/7"),
            types.InlineKeyboardButton("❗ Rules", url="https://t.me/c/3056610802/13")
        )
        markup.add(
            types.InlineKeyboardButton("⭐ Reviews", url="https://t.me/c/3056610802/3"),
            types.InlineKeyboardButton("🎁 Giveaways", url="https://t.me/c/3056610802/2")
        )
        markup.add(
            types.InlineKeyboardButton("📢 Announcements", url="https://t.me/c/3056610802/9")
        )
        markup.add(
            types.InlineKeyboardButton("🍴 Place your order – Reserve with £50 off", url="https://t.me/axel_fork_bot")
        )

        # Welcome message
        welcome_text = (
            f"✨ Welcome to Golden Fork, $username *{username}* ✨\n"
            f"The place where every reservation means £50 in savings*\n\n"
            f"Main Sections:\n"
            f"ℹ️ Service Info | ❗ Rules | ⭐ Reviews | 🎁 Giveaways | 📢 Announcements\n\n"
            f"👉 To get started::"
        )

        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- START BOT ---
if __name__ == "__main__":
    print("🤖 Welcome bot is running...")
    bot.polling(none_stop=True)
