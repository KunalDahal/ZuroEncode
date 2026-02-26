import os
import shutil

class Uploader:
    def __init__(self, client, task_data: dict):
        self.client = client
        self.task_data = task_data
        self.upload_progress = {
            "total_size": 0,
            "uploaded": 0,
            "percentage": 0,
            "speed": 0,
            "remaining": 0,
            "status": "idle"
        }

    async def upload(self):
        task_id = self.task_data["task_id"]
        user_id = self.task_data["user_id"]
        output_file_name = self.task_data["output_filename"]
        send_type = self.task_data.get("send_type", "media")
        thumbnail_path = self.task_data.get("thumbnail_path", "")
        
        task_folder = os.path.join("./src/bin/tmp", task_id)
        
        encoded_files = [f for f in os.listdir(task_folder) if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))]
        
        if not encoded_files:
            raise Exception("No encoded file found in task folder")
        
        current_file = os.path.join(task_folder, encoded_files[0])
        final_file_path = os.path.join(task_folder, output_file_name)

        if current_file != final_file_path:
            shutil.move(current_file, final_file_path)
        
        if not os.path.exists(final_file_path):
            raise Exception("File not found after renaming")
        
        file_size = os.path.getsize(final_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        self.upload_progress["total_size"] = file_size
        self.upload_progress["status"] = "uploading"
        
        try:
            caption = (
                f"`{output_file_name}`\n"
            )
            
            thumb = thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None
            
            if send_type.lower() in ["doc", "document"]:
                result = await self.client.send_document(
                    chat_id=user_id,
                    document=final_file_path,
                    thumb=thumb,
                    caption=caption,
                    force_document=True, 
                    file_name=output_file_name,
                    progress=self._progress_callback
                )
            else:
                result = await self.client.send_video(
                    chat_id=user_id,
                    video=final_file_path,
                    thumb=thumb,
                    caption=caption,
                    supports_streaming=True,
                    progress=self._progress_callback
                )
            
            self.upload_progress["status"] = "completed"
            return result
            
        except Exception as e:
            self.upload_progress["status"] = "failed"
            error_msg = f"Upload failed: {str(e)}"
            raise Exception(error_msg)

    async def _progress_callback(self, current, total):
        if total > 0:
            percentage = (current / total) * 100
            self.upload_progress.update({
                "uploaded": current,
                "percentage": round(percentage, 2),
                "remaining": total - current,
                "total_size": total
            })
            
            if int(percentage) % 10 == 0 and int(percentage) > 0:
                percentage_str = f"{percentage:.2f}%"

    def get_progress(self) -> dict:
        return self.upload_progress.copy()