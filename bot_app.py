import os
import json
import requests
import telebot

# Ambil token dari environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Init bot Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# File untuk simpan interaksi user
DB_FILE = "db.json"

# Load database sederhana
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"users": {}}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Fungsi kirim ke OpenAI GPT
def ask_gpt(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are OmniSocial Strategist Free Version. Jawab modular, ringkas, beri teaser supaya user penasaran. Free hanya 10 sesi."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# Handle pesan masuk
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = str(message.chat.id)
    user_text = message.text

    # Load db & hitung interaksi
    db = load_db()
    users = db["users"]
    if chat_id not in users:
        users[chat_id] = {"count": 0}
    users[chat_id]["count"] += 1
    save_db(db)

    # Cek limit 10 sesi
    if users[chat_id]["count"] > 10:
        bot.send_message(
            chat_id,
            "🚀 Kamu sudah menggunakan 10 sesi gratis.\n\nMau lanjut tanpa batas? Upgrade Premium & dapatkan link GPT versi full 👉 https://wa.me/6289518935001?text=Halo%20aku%20mau%20upgrade%20akses%20premium%20OmniSocial%20Strategist!"
        )
        return

    # Kalau masih <=10, kirim ke GPT
    reply = ask_gpt(user_text)
    bot.send_message(chat_id, reply)

# Jalankan bot
if __name__ == "__main__":
    print("🤖 Bot Telegram berjalan...")
    bot.polling()
