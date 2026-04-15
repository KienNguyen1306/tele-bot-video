import json
import os
import random
import string
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TOKEN
STORAGE_FILE = "videos.json"
TARGET_CHAT_ID = -1003707496482  # 👉 thay bằng ID group của bạn


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


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    video = msg.video or msg.document
    if not video:
        return

    file_id = video.file_id

    # tạo key + lưu
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

    # ✅ xử lý thumbnail (ảnh)
    if msg.video and msg.video.thumbnail:
        thumb = msg.video.thumbnail

        # tải ảnh về
        file = await context.bot.get_file(thumb.file_id)
        path = f"{thumb.file_id}.jpg"
        await file.download_to_drive(path)

        # gửi ảnh sang group
        await context.bot.send_photo(
            chat_id=TARGET_CHAT_ID,
            photo=open(path, "rb"),
            caption=caption
        )

        # xóa file
        os.remove(path)

    else:
        # nếu không có thumbnail thì gửi video luôn
        await context.bot.send_video(
            chat_id=TARGET_CHAT_ID,
            video=file_id,
            caption=caption
        )

    # reply user
    await msg.reply_text(
        f"✅ Đã lưu!\n"
        f"📝 Caption: {msg.caption or 'Không có'}\n"
        f"🔗 https://t.me/{bot_username}?start={key}"
    )
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(
    filters.VIDEO | filters.Document.ALL, handle_video))

print("✅ Đang chờ video...")
app.run_polling()
