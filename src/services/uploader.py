from pyrogram import Client
from pyrogram.types import Message
from typing import Optional

class Uploader:
    def __init__(self, client: Client):
        self.client = client

    async def upload_video(self, chat_id: int, file_path: str, caption: Optional[str] = None) -> Message:
        try:
            return await self.client.send_video(
                chat_id=chat_id,
                video=file_path,
                caption=caption
            )
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")