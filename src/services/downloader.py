import os
from typing import Optional
from pyrogram import Client

class Downloader:
    def __init__(self, temp_dir: str = "./src/temp/"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    async def download(self, client: Client, file_id: str, filename: Optional[str] = None) -> str:
        if not filename:
            filename = f"download_{file_id[:8]}.tmp"
        
        file_path = os.path.join(self.temp_dir, filename)
        
        try:
            await client.download_media(file_id, file_name=file_path)
            return file_path
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")