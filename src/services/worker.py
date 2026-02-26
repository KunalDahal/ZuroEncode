import asyncio
import os
import shutil
import logging
from datetime import datetime
import concurrent.futures

class Worker:
    def __init__(self, task_queue, user_settings_getter, ffmpeg, client):
        self.task_queue = task_queue
        self.user_settings_getter = user_settings_getter
        self.ffmpeg = ffmpeg
        self.client = client
        self.temp_base = "./src/bin/tmp"
        self.running = False
        self.current_task = None
        self.current_task_id = None
        self.processing_task = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        
        os.makedirs(self.temp_base, exist_ok=True)

    async def process_task(self, task: dict):
        task_id = task["task_id"]
        task_folder = os.path.join(self.temp_base, task_id)
        
        downloaded_path = None
        encoded_path = None
        
        try:
            task["started_at"] = datetime.utcnow().isoformat()
            
            self.task_queue.update_status(task_id, "downloading", 10)
            
            from src.services.downloader import Downloader
            downloader = Downloader(self.temp_base)
            downloaded_path = await downloader.download(
                client=self.client,
                task_data=task
            )
            
            if not downloaded_path or not os.path.exists(downloaded_path):
                raise Exception("Download failed: file not found")

            self.task_queue.update_status(task_id, "encoding", 40)
            
            user_settings = self.user_settings_getter(task["user_id"])
            settings = user_settings.get()
            
            from src.services.encoder import Encoder
            encoder = Encoder(self.ffmpeg)
            
            loop = asyncio.get_event_loop()
            encoded_path = await loop.run_in_executor(
                self.executor,
                self._run_encoding_sync,
                encoder, task, downloaded_path, settings
            )
            
            if not encoded_path or not os.path.exists(encoded_path):
                raise Exception("Encoding failed: output file not found")

            self.task_queue.update_status(task_id, "uploading", 80)
            
            from src.services.uploader import Uploader
            uploader = Uploader(self.client, task)
            await uploader.upload()

            self.task_queue.remove_task(task_id)
            
            await self.notify_user(
                task["user_id"], 
                f"✅ Task Completed Successfully\n📁 {task['output_filename']}\n🆔 {task_id[:8]}"
            )

        except asyncio.CancelledError:
            await self.notify_user(
                task["user_id"],
                f"❌ Task Cancelled\n🆔 {task_id[:8]}"
            )
            self.task_queue.remove_task(task_id)
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Task {task_id} failed: {error_msg}")
            await self.notify_user(
                task["user_id"], 
                f"❌ Task Failed\nError: {error_msg[:100]}\n🆔 {task_id[:8]}"
            )
            self.task_queue.remove_task(task_id)
        
        finally:
            for file_path in [downloaded_path, encoded_path]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            if os.path.exists(task_folder):
                try:
                    shutil.rmtree(task_folder)
                except:
                    pass
            
            self.current_task_id = None
            self.current_task = None
            self.task_queue.set_processing(False)

    def _run_encoding_sync(self, encoder, task, downloaded_path, settings):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                encoder.encode(
                    task_data=task,
                    input_path=downloaded_path,
                    settings=settings
                )
            )
        finally:
            loop.close()