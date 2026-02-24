import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID", "0"))


def setup_encode_handlers(app: Client, task_queue, user_settings, downloader, encoder, uploader, ffmpeg):
    
    @app.on_message(filters.command("e") & filters.group)
    async def encode_command(client: Client, message: Message):
        if message.chat.id != ALLOWED_GROUP_ID:
            await message.reply_text("This bot only works in the designated group.")
            return

        if not message.reply_to_message:
            await message.reply_text("Please reply to a video file with /e outputname")
            return

        replied = message.reply_to_message
        has_video = (
            replied.video or 
            (replied.document and replied.document.mime_type and 
             replied.document.mime_type.startswith("video/"))
        )
        
        if not has_video:
            await message.reply_text("Please reply to a video file.")
            return

        if len(message.command) < 2:
            await message.reply_text("Please provide output filename.\nExample: /e myvideo.mp4")
            return

        output_filename = message.command[1]
        if not any(output_filename.endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov']):
            output_filename += '.mkv'

        file_id = None
        original_filename = "video.mp4"
        
        if replied.video:
            file_id = replied.video.file_id
            original_filename = replied.video.file_name or f"video_{file_id[:8]}.mp4"
        elif replied.document:
            file_id = replied.document.file_id
            original_filename = replied.document.file_name or f"video_{file_id[:8]}.mp4"

        # Create task
        task_id = task_queue.create_task(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            file_id=file_id,
            original_filename=original_filename,
            output_filename=output_filename
        )

        await message.reply_text(
            f"Task created! : `{task_id[:8]}` \n"
            f"Output Name: `{output_filename}`\n"
            f"Position: {task_queue.get_queued_count()}"
        )