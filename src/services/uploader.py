from pyrogram import Client
from pyrogram.types import Message
from typing import Optional

class Uploader:
    def __init__(self, client: Client):
        self.client = client

    async def upload_video(self, chat_id: int, file_path: str, output_file_name: str, task_id: str) -> Message:
        try:
            return await self.client.send_video(
                chat_id=chat_id,
                video=file_path,
                caption=f"✅ Encoded: {output_file_name}\nTask: `{task_id[:8]}`"
            )
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")