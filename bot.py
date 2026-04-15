import random
import string
import mysql.connector

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

from config import TOKEN, TARGET_CHAT_IDS, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# =========================
# MYSQL CONNECTION
# =========================
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)


cur = db.cursor()


# =========================
# RANDOM KEY (MYSQL CHECK)
# =========================
def random_key(length=6):
    while True:
        key = ''.join(random.choices(
            string.ascii_letters + string.digits, k=length
        ))

        cur.execute("SELECT `key` FROM videos WHERE `key`=%s", (key,))
        if not cur.fetchone():
            return key


# =========================
# HANDLE VIDEO
# =========================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    video = msg.video or msg.document
    if not video:
        return

    file_id = video.file_id
    caption = msg.caption or ""

    key = random_key()
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={key}"

    # =========================
    # SAVE TO MYSQL
    # =========================
    sql = """
        INSERT INTO videos (`key`, file_id, caption, link)
        VALUES (%s, %s, %s, %s)
    """
    val = (key, file_id, caption, link)

    cur.execute(sql, val)
    db.commit()

    full_caption = f"{caption}\n\n🔗 {link}"

    # =========================
    # SEND TO TARGET CHATS
    # =========================
    if msg.video and msg.video.thumbnail:
        thumb = msg.video.thumbnail
        file = await context.bot.get_file(thumb.file_id)

        path = f"{thumb.file_id}.jpg"
        await file.download_to_drive(path)

        for chat_id in TARGET_CHAT_IDS:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=open(path, "rb"),
                caption=full_caption
            )

        import os
        os.remove(path)

    else:
        for chat_id in TARGET_CHAT_IDS:
            await context.bot.send_video(
                chat_id=chat_id,
                video=file_id,
                caption=full_caption
            )

    await msg.reply_text(
        f"✅ Đã lưu MySQL!\n"
        f"🔑 Key: {key}\n"
        f"🔗 {link}"
    )


# =========================
# HANDLE START (/start key)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = context.args[0] if context.args else None

    if payload:
        cur.execute(
            "SELECT file_id, caption FROM videos WHERE `key`=%s",
            (payload,)
        )
        row = cur.fetchone()

        if row:
            file_id, caption = row

            await update.message.reply_video(
                video=file_id,
                caption=caption
            )
        else:
            await update.message.reply_text("❌ Không tìm thấy video.")
    else:
        await update.message.reply_text("👋 Xin chào!")


# =========================
# RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(
    filters.VIDEO | filters.Document.ALL,
    handle_video
))

print("✅ Bot đang chạy MySQL...")
app.run_polling()
