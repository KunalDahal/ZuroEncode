import asyncio
import os
import shutil
from pyrogram import Client
from src import (
    Downloader,
    Encoder,
    Uploader,
)


class Worker:
    def __init__(self, task_queue, user_settings, ffmpeg, client: Client):
        self.task_queue = task_queue
        self.user_settings = user_settings
        self.ffmpeg = ffmpeg
        self.client = client
        self.temp_dir = "./src/log/tmp"
        self.running = False
        self.current_task = None
        
        os.makedirs(self.temp_dir, exist_ok=True)

    async def start(self):
        self.running = True
        while self.running:
            try:
                if not self.current_task and not self.task_queue.is_processing():
                    next_task = self.task_queue.get_next_task()
                    if next_task:
                        self.current_task = next_task
                        self.task_queue.set_processing(True)
                        asyncio.create_task(self.process_task(self.current_task))
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False

    async def process_task(self, task: dict):
        task_id = task["task_id"]
        task_dir = None
        
        try:
            await self.notify_user(task["chat_id"], f"✅ Task queued: {task['output_file_name']}")
            
            self.task_queue.update_status(task_id, "downloading")
            await self.notify_user(task["chat_id"], f"⏬ Downloading: {task['original_file_name']}")
            
            downloader = Downloader(self.temp_dir)
            task_dir, was_split = await downloader.download(
                self.client, 
                task_id, 
                task["file_id"], 
                task["original_file_name"],
                task["split_size"]
            )

            self.task_queue.update_status(task_id, "encoding")
            await self.notify_user(task["chat_id"], f"🎬 Encoding: {task['output_file_name']}")
            
            settings = self.user_settings.get(task["user_id"])
            
            encoder = Encoder(self.ffmpeg)
            output_path = await encoder.encode(
                task_dir, 
                task_id, 
                task["original_file_name"], 
                task["output_file_name"], 
                settings
            )

            self.task_queue.update_status(task_id, "uploading")
            await self.notify_user(task["chat_id"], f"📤 Uploading: {task['output_file_name']}")
            
            uploader = Uploader(self.client)
            await uploader.upload_video(
                chat_id=task["chat_id"],
                file_path=output_path,
                output_file_name=task["output_file_name"],
                task_id=task_id
            )

            self.task_queue.remove_task(task_id)
            await self.notify_user(task["chat_id"], f"✅ Task completed: {task['output_file_name']}")

        except Exception as e:
            error_msg = str(e)
            await self.notify_user(task["chat_id"], f"❌ Task failed: {error_msg}")
            self.task_queue.remove_task(task_id)
        
        finally:
            if task_dir and os.path.exists(task_dir):
                try:
                    shutil.rmtree(task_dir)
                except:
                    pass
            
            self.current_task = None
            self.task_queue.set_processing(False)

    async def notify_user(self, chat_id: int, message: str):
        try:
            await self.client.send_message(chat_id, message)
        except:
            pass