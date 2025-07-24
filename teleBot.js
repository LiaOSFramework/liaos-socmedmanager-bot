import TelegramBot from "node-telegram-bot-api";
import axios from "axios";
import { Low, JSONFile } from "lowdb";

// Ambil token dari environment (Streamlit Secrets nanti)
const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const OPENAI_KEY = process.env.OPENAI_KEY;

// DB interaksi user
const adapter = new JSONFile('db.json');
const db = new Low(adapter, { users: {} });
await db.read();

const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on("message", async (msg) => {
  const chatId = msg.chat.id;
  const text = msg.text;

  // Hitung interaksi user
  let user = db.data.users[chatId] || { count: 0 };
  user.count += 1;
  db.data.users[chatId] = user;
  await db.write();

  // Jika sudah lewat 10 sesi => upsell
  if (user.count > 10) {
    bot.sendMessage(
      chatId,
      "🚀 Kamu sudah menggunakan 10 sesi gratis. Mau lanjut tanpa batas? Upgrade Premium & dapatkan link GPT versi full 👉 https://wa.me/6289518935001?text=Halo%20aku%20mau%20upgrade%20akses%20premium%20OmniSocial%20Strategist!"
    );
    return;
  }

  // Kalau masih ≤10 => kirim ke OpenAI GPT
  const response = await axios.post(
    "https://api.openai.com/v1/chat/completions",
    {
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: "You are OmniSocial Strategist Free Version. Jawab modular, ringkas, beri teaser supaya user penasaran. Free hanya 10 sesi."
        },
        { role: "user", content: text }
      ],
    },
    {
      headers: {
        "Authorization": `Bearer ${OPENAI_KEY}`,
        "Content-Type": "application/json",
      },
    }
  );

  const reply = response.data.choices[0].message.content;
  bot.sendMessage(chatId, reply);
});
