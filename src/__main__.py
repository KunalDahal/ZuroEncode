import asyncio
import os
import logging
from pyrogram import Client, idle, filters
from pyrogram.types import Message

from src import Config, TaskQueue, UserSettings, FFmpeg
from src.services import Worker
from src.handlers.encode import setup_encode_handlers
from src.handlers.settings import setup_settings_handlers
from src.handlers.status import setup_status_handlers

logging.basicConfig(level=logging.INFO)

sessions_dir = "./src/bin/logs/"
os.makedirs(sessions_dir, exist_ok=True)

async def main():
    config = Config()
    
    app = Client(
        "encode_bot_session",
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
        workdir=sessions_dir
    )
    
    task_queue = TaskQueue()
    ffmpeg = FFmpeg()
    user_settings_cache = {}
    
    def get_user_settings(user_id):
        if user_id not in user_settings_cache:
            user_settings_cache[user_id] = UserSettings(user_id)
        return user_settings_cache[user_id]
    
    await app.start()
    print(f"✅ Bot started: @{(await app.get_me()).username}")
    
    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        if message.from_user.id in config.admin_ids:
            await message.reply_text(
                "✅ **Welcome Admin!**\n\n"
                "Available commands:\n"
                "• /encode - Encode a video (reply to video)\n"
                "• /s - Check queue status\n"
                "• /us - View/change encoding settings\n"
                "• /cancel - Cancel current input"
            )
        else:
            await message.reply_text("❌ You are not authorized to use this bot.")
    
    @app.on_message(filters.command("encode") & filters.private)
    async def encode_private(client: Client, message: Message):
        if message.from_user.id not in config.admin_ids:
            await message.reply_text("❌ You are not authorized to use this command.")
            return
            
        if not message.reply_to_message:
            await message.reply_text("Please reply to a video file.")
            return
        
        await handle_encode_in_dm(client, message, task_queue, get_user_settings)
    
    setup_encode_handlers(
        app=app,
        task_queue=task_queue,
        user_settings=get_user_settings
    )
    
    setup_settings_handlers(
        app=app,
        user_settings=get_user_settings
    )
    
    setup_status_handlers(
        app=app,
        task_queue=task_queue,
        admin_ids=config.admin_ids
    )
    
    worker = Worker(task_queue, get_user_settings, ffmpeg, app)
    asyncio.create_task(worker.start())
    
    await idle()
    
    await app.stop()

async def handle_encode_in_dm(client: Client, message: Message, task_queue, user_settings):
    from src.handlers.encode import process_encode_command
    await process_encode_command(client, message, task_queue, user_settings)

if __name__ == "__main__":
    asyncio.run(main())