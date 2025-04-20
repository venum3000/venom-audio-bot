import os
import random
import asyncio
from flask import Flask, render_template, send_from_directory
from telebot.async_telebot import AsyncTeleBot
from telebot import types

TOKEN = os.getenv("7601773504:AAEzmErTREEAlbjoAqf7VcN8XNt_1Cbwnzw")
CHANNEL_ID = os.getenv("@ainkrad01")

bot = AsyncTeleBot(TOKEN)
app = Flask(__name__)

AUDIO_FOLDER = "audio"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio/<path:filename>')
def download_file(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

def get_random_audio():
    files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.mp3')]
    if not files:
        return None
    return random.choice(files)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Перейти в канал', url=f'https://t.me/{CHANNEL_ID}')
    markup.add(btn)

    member = await bot.get_chat_member(f"@{CHANNEL_ID}", message.from_user.id)
    if member.status in ['left', 'kicked']:
        await bot.send_message(message.chat.id, "Подпишись на наш канал, чтобы получить доступ к боту!", reply_markup=markup)
        return
    
    await bot.send_message(message.chat.id, "Добро пожаловать! Жми /audio чтобы получить аудиофайл!")

@bot.message_handler(commands=['audio'])
async def send_audio(message):
    loading = await bot.send_message(message.chat.id, "Ищем аудио... 🔄")
    await asyncio.sleep(2)  # типа "анимация ожидания"

    audio_file = get_random_audio()
    if audio_file:
        with open(os.path.join(AUDIO_FOLDER, audio_file), 'rb') as f:
            await bot.send_audio(message.chat.id, f)
    else:
        await bot.send_message(message.chat.id, "Нет доступных аудиофайлов 😢")
    
    await bot.delete_message(message.chat.id, loading.message_id)

async def main():
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
