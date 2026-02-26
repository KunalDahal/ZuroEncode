import os
import asyncio

class Downloader:
    def __init__(self, temp_base: str):
        self.temp_base = temp_base
        os.makedirs(self.temp_base, exist_ok=True)
        self.download_progress = {
            "total_size": 0,
            "downloaded": 0,
            "percentage": 0,
            "speed": 0,
            "remaining": 0,
            "status": "idle"
        }

    async def download(self, client, task_data: dict) -> str:
        task_id = task_data["task_id"]
        file_id = task_data["file_id"]
        original_file_name = task_data["original_file_name"]
        
        task_folder = os.path.join(self.temp_base, task_id)
        os.makedirs(task_folder, exist_ok=True)
        
        file_path = os.path.join(task_folder, original_file_name)
        
        try:
            self._reset_progress()
            self.download_progress["status"] = "downloading"
            
            await asyncio.wait_for(
                client.download_media(
                    file_id, 
                    file_name=file_path,
                    progress=self._progress_callback
                ),
                timeout=300
            )
            
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                raise Exception("Downloaded file not found or empty")
            
            self.download_progress["status"] = "completed"
            return file_path
                
        except asyncio.TimeoutError:
            self.download_progress["status"] = "failed"
            raise Exception("Download timeout")
        except Exception as e:
            self.download_progress["status"] = "failed"
            raise Exception(f"Download failed: {str(e)}")

    def _reset_progress(self):
        self.download_progress = {
            "total_size": 0,
            "downloaded": 0,
            "percentage": 0,
            "speed": 0,
            "remaining": 0,
            "status": "idle"
        }

    async def _progress_callback(self, current, total):
        if total > 0:
            percentage = (current / total) * 100
            self.download_progress.update({
                "total_size": total,
                "downloaded": current,
                "percentage": round(percentage, 2),
                "remaining": total - current,
                "status": "downloading"
            })

    def get_progress(self) -> dict:
        return self.download_progress.copy()