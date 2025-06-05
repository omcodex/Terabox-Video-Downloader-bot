import os import logging import asyncio import aiohttp import json import uuid from dotenv import load_dotenv from aiogram import Bot, Dispatcher, types from aiogram.types import FSInputFile from aiogram.utils import executor

.env से टोकन लोड करें

load_dotenv() BOT_TOKEN = os.getenv("BOT_TOKEN")

लॉग सेटअप

logging.basicConfig(level=logging.INFO)

Bot और Dispatcher

bot = Bot(token=BOT_TOKEN) dp = Dispatcher(bot)

यूजर लिमिट फाइल

LIMIT_FILE = "limits.json"

लिमिट लोड या इनिशियलाइज़

if os.path.exists(LIMIT_FILE): with open(LIMIT_FILE, 'r') as f: user_limits = json.load(f) else: user_limits = {}

हर यूजर की डिफ़ॉल्ट लिमिट

DEFAULT_LIMIT = 5

लिमिट सेव करने का फ़ंक्शन

def save_limits(): with open(LIMIT_FILE, 'w') as f: json.dump(user_limits, f)

फेक डाउनलोड फ़ंक्शन (Demo के लिए)

async def download_video(url, user_id): filename = f"video_{uuid.uuid4().hex[:8]}.mp4" async with aiohttp.ClientSession() as session: async with session.get("https://file-examples.com/storage/fed8fb8d5a9277c23534b79/2017/04/file_example_MP4_480_1_5MG.mp4") as resp: with open(filename, 'wb') as f: while True: chunk = await resp.content.read(1024) if not chunk: break f.write(chunk) return filename

यूजर का उपयोग बढ़ाना और चेक करना

def increment_usage(user_id): user_id = str(user_id) if user_id not in user_limits: user_limits[user_id] = {"used": 0, "limit": DEFAULT_LIMIT} user_limits[user_id]["used"] += 1 save_limits()

def can_download(user_id): user_id = str(user_id) if user_id not in user_limits: return True return user_limits[user_id]["used"] < user_limits[user_id]["limit"]

/start कमांड

@dp.message_handler(commands=['start']) async def send_welcome(message: types.Message): await message.reply("नमस्ते! TeraBox लिंक भेजिए और मैं वीडियो भेज दूंगा।")

/usage कमांड

@dp.message_handler(commands=['usage']) async def usage_info(message: types.Message): user_id = str(message.from_user.id) used = user_limits.get(user_id, {}).get("used", 0) limit = user_limits.get(user_id, {}).get("limit", DEFAULT_LIMIT) await message.reply(f"आपने {used}/{limit} बार उपयोग किया है।")

लिंक हैंडलर

@dp.message_handler(lambda message: message.text and "terabox" in message.text) async def handle_link(message: types.Message): user_id = message.from_user.id

if not can_download(user_id):
    await message.reply("आपका फ्री लिमिट समाप्त हो गया है।")
    return

await message.reply("वीडियो डाउनलोड हो रहा है, कृपया प्रतीक्षा करें...")
video_file = await download_video(message.text, user_id)

try:
    await message.reply_document(FSInputFile(video_file))
    increment_usage(user_id)
except Exception as e:
    await message.reply("वीडियो भेजने में समस्या हुई।")
finally:
    if os.path.exists(video_file):
        os.remove(video_file)

रन

if name == 'main': executor.start_polling(dp, skip_updates=True)

