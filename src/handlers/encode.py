import os
import uuid
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from dotenv import load_dotenv

load_dotenv()
ALLOWED_GROUP_IDS = [int(id.strip()) for id in os.getenv("ALLOWED_GROUP_IDS", "0").split(",") if id.strip()]
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi', '.mpeg', '.mpg', '.wmv', '.flv', '.3gp'}


def setup_encode_handlers(app: Client, task_queue, user_settings, downloader, encoder, uploader, ffmpeg):
    
    @app.on_message(filters.command("encode") & filters.group)
    async def encode_command(client: Client, message: Message):
        if message.chat.id not in ALLOWED_GROUP_IDS:
            await message.reply_text("This command is not allowed here.")
            return

        bot_is_premium = client.me.is_premium if client.me else False
        split_size = 3.95 * 1024 * 1024 * 1024 if bot_is_premium else 1.95 * 1024 * 1024 * 1024  # Convert to bytes

        if len(message.command) < 2:
            await message.reply_text(
                "Please provide an output filename.\n"
                "Usage: `/encode <output_filename>`\n"
                "Example: `/encode movie.mp4`"
            )
            return

        output_filename = message.command[1]

        try:
            await client.send_chat_action(message.from_user.id, "typing")
        except Exception:
            await message.reply_text(
                "Please start the bot in private chat first.\n"
                "1. Click on my username\n"
                "2. Press 'Start' or send /start\n"
                "3. Then try this command again"
            )
            return

        if not message.reply_to_message:
            await message.reply_text("Reply to a video file.")
            return

        replied = message.reply_to_message
        file_id = None
        original_file_name = None
        file_size = None
        media_type = None

        if replied.video:
            media_type = "video"
            file_id = replied.video.file_id
            original_file_name = replied.video.file_name or f"video_{file_id[:8]}.mp4"
            file_size = replied.video.file_size
            
        elif replied.document:
            file_name = replied.document.file_name or ""
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext in ALLOWED_VIDEO_EXTENSIONS:
                media_type = "document"
                file_id = replied.document.file_id
                original_file_name = replied.document.file_name or f"video_{file_id[:8]}{file_ext}"
                file_size = replied.document.file_size
            else:
                await message.reply_text("Invalid file type. Only video files are allowed.")
                return
        else:
            await message.reply_text("Only video files are allowed.")
            return

        task_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        task_data = {
            "task_id": task_id,
            "user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "file_id": file_id,
            "original_file_name": original_file_name,
            "output_filename": output_filename,
            "split_size": split_size,
            "status": "queued",
            "created_at": created_at,
            "media_type": media_type,
            "file_size": file_size
        }
        
        # Add task to queue
        task_queue.add_task(task_data)
        task_queue.update_status(task_id, "queued")
        position = task_queue.get_queue_position(task_id)

        await message.reply_text(
            f"**Task Created Successfully**\n\n"
            f"🆔 **Task ID:** `{task_id[:8]}`\n"
            f"📁 **Output:** `{output_filename}`\n"
            f"📍 **Queue Position:** `{position}`\n\n"
            f"_Your file will be sent to you in private chat once processing is complete._"
        )