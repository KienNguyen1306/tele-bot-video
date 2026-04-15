import json
import os
import random
import string
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from config import TOKEN, TARGET_CHAT_ID

STORAGE_FILE = "videos.json"


def load():
    return json.load(open(STORAGE_FILE)) if os.path.exists(STORAGE_FILE) else {}


def save(data):
    json.dump(data, open(STORAGE_FILE, "w"), indent=2)


def random_key(data, length=6):
    while True:
        key = ''.join(random.choices(
            string.ascii_letters + string.digits, k=length))
        if key not in data:
            return key


videos = load()


# 🔥 HANDLE VIDEO
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    video = msg.video or msg.document
    if not video:
        return

    file_id = video.file_id

    key = random_key(videos)
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={key}"

    videos[key] = {
        "file_id": file_id,
        "caption": msg.caption or "",
        "link": link
    }
    save(videos)
    caption = (
        f"{msg.caption or ''}\n\n"
        f"🔗 {link}"
    )

    # gửi ảnh preview
    if msg.video and msg.video.thumbnail:
        thumb = msg.video.thumbnail
        file = await context.bot.get_file(thumb.file_id)

        path = f"{thumb.file_id}.jpg"
        await file.download_to_drive(path)

        await context.bot.send_photo(
            chat_id=TARGET_CHAT_ID,
            photo=open(path, "rb"),
            caption=caption
        )

        os.remove(path)
    else:
        await context.bot.send_video(
            chat_id=TARGET_CHAT_ID,
            video=file_id,
            caption=caption
        )

    await msg.reply_text(
        f"✅ Đã lưu!\n"
        f"🔑 Key: {key}\n"
        f"🔗 https://t.me/{bot_username}?start={key}"
    )


# 🔥 HANDLE START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    VIDEO_MAP = load()
    payload = context.args[0] if context.args else None

    if payload and payload in VIDEO_MAP:
        data = VIDEO_MAP[payload]

        await update.message.reply_video(
            video=data["file_id"],
            caption=data.get("caption", "")
        )
    elif payload:
        await update.message.reply_text("❌ Không tìm thấy video.")
    else:
        await update.message.reply_text("👋 Xin chào!")


# 🚀 RUN BOT
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(
    filters.VIDEO | filters.Document.ALL, handle_video))

print("✅ Bot đang chạy...")
app.run_polling()
