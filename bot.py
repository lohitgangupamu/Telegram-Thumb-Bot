import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen

BOT_TOKEN = "7365620276:AAGuh0mvjHoY6_ZXhzsxaUA6NzIlzE3-0Mw"
API_ID = "27727369"
API_HASH = "1a6616b34f66ed256a8330ad9cb674ed"

Bot = Client(
    "Thumb-Bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

START_TXT = "Hi {}, I am a bulk video thumbnail changer bot.\n\nSend all videos at once, then send a thumbnail."

START_BTN = InlineKeyboardMarkup(
    [[InlineKeyboardButton('Source Code', url='https://github.com/soebb/thumb-change-bot')]]
)

@Bot.on_message(filters.command(["start"]))
async def start(bot, update):
    await update.reply_text(
        text=START_TXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=START_BTN
    )

# Store file paths in a list
video_files = []

@Bot.on_message(filters.private & (filters.video | filters.document))
async def collect_videos(bot, m):
    global video_files
    msg = await m.reply("`Downloading file...`")
    
    file_path = await bot.download_media(message=m)
    video_files.append((m, file_path))  # Store message & file path
    
    await msg.edit("✅ File received! Send more or send the thumbnail.")

@Bot.on_message(filters.private & filters.photo)
async def process_videos(bot, m):
    global video_files
    
    # If no videos were sent before, ignore
    if not video_files:
        await m.reply("❌ No videos received! Please send videos first.")
        return
    
    # Download the thumbnail
    thumb_path = await bot.download_media(message=m)

    await m.reply("🔄 Processing all videos with the new thumbnail...")

    # Loop through all stored videos and process them
    for msg, file_path in video_files:
        await bot.send_video(
            chat_id=msg.chat.id,
            video=file_path,
            thumb=thumb_path,
            caption=msg.caption if msg.caption else "Here is your updated video!"
        )
        os.remove(file_path)

    # Cleanup
    os.remove(thumb_path)
    video_files.clear()  # Reset list for the next batch
    await m.reply("✅ All videos processed successfully!")

Bot.run()
