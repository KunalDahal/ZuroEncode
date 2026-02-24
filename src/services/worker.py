import asyncio
import os
import tempfile
import shutil
from pyrogram import Client


class Worker:
    def __init__(self, task_queue, user_settings, ffmpeg, client: Client, temp_dir: str):
        self.task_queue = task_queue
        self.user_settings = user_settings
        self.ffmpeg = ffmpeg
        self.client = client
        self.temp_dir = temp_dir
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                if not self.task_queue.is_processing():
                    next_task = self.task_queue.get_next_task()
                    if next_task:
                        asyncio.create_task(self.process_task(next_task))
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False

    async def process_task(self, task: dict):
        task_id = task["task_id"]
        temp_work_dir = None
        
        try:
            # Create temp directory for this task
            temp_work_dir = tempfile.mkdtemp(dir=self.temp_dir)
            input_path = os.path.join(temp_work_dir, "input_" + task["original_filename"])
            output_path = os.path.join(temp_work_dir, task["output_filename"])

            # DOWNLOADING
            self.task_queue.update_status(task_id, "downloading")
            await self.notify_user(task["chat_id"], f"⏬ Downloading: {task['original_filename']}")
            
            await self.client.download_media(task["file_id"], file_name=input_path)

            # ENCODING
            self.task_queue.update_status(task_id, "encoding")
            await self.notify_user(task["chat_id"], f"🎬 Encoding: {task['output_filename']}")
            
            settings = self.user_settings.get(task["user_id"])
            success = await self.ffmpeg.execute(
                self.ffmpeg.build_command(input_path, output_path, settings)
            )
            
            if not success:
                raise Exception("Encoding failed")

            # UPLOADING
            self.task_queue.update_status(task_id, "uploading")
            await self.notify_user(task["chat_id"], f"📤 Uploading: {task['output_filename']}")
            
            await self.client.send_video(
                chat_id=task["chat_id"],
                video=output_path,
                caption=f"✅ Encoded: {task['output_filename']}\nTask: `{task_id[:8]}`"
            )

            self.task_queue.remove_task(task_id)
            await self.notify_user(task["chat_id"], f"✅ Task completed: {task['output_filename']}")

        except Exception as e:
            error_msg = str(e)
            self.task_queue.update_status(task_id, "failed", error_msg)
            await self.notify_user(
                task["chat_id"],
                f"❌ Task failed: {error_msg}\nTask: `{task_id[:8]}`"
            )
            self.task_queue.remove_task(task_id)
        
        finally:
            if temp_work_dir and os.path.exists(temp_work_dir):
                try:
                    shutil.rmtree(temp_work_dir)
                except:
                    pass

    async def notify_user(self, chat_id: int, message: str):
        try:
            await self.client.send_message(chat_id, message)
        except:
            pass