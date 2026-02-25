import os
import asyncio
from typing import Optional, Tuple
from pyrogram import Client

class Downloader:
    def __init__(self, temp_dir: str = "./src/log/tmp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    async def download(self, client: Client, task_id: str, file_id: str, original_file_name: str, split_size: int) -> Tuple[str, bool]:
        task_dir = os.path.join(self.temp_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        temp_path = os.path.join(task_dir, f"{task_id}_original.tmp")
        
        try:
            await client.download_media(file_id, file_name=temp_path)
            file_size = os.path.getsize(temp_path)
            
            if file_size > split_size:
                num_parts = (file_size + split_size - 1) // split_size
                
                with open(temp_path, 'rb') as f:
                    for i in range(num_parts):
                        part_path = os.path.join(task_dir, f"{task_id}_part{i:03d}")
                        with open(part_path, 'wb') as part:
                            part.write(f.read(split_size))
                
                os.remove(temp_path)
                return task_dir, True
            else:
                final_path = os.path.join(task_dir, original_file_name)
                os.rename(temp_path, final_path)
                return task_dir, False
                
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")