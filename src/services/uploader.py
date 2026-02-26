import os
import shutil
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Find encoded files
        encoded_files = [f for f in os.listdir(task_folder) if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))]
        
        if not encoded_files:
            raise Exception("No encoded file found in task folder")
        
        logger.info(f"Found encoded files: {encoded_files}")
        
        current_file = os.path.join(task_folder, encoded_files[0])
        final_file_path = os.path.join(task_folder, output_file_name)
        
        # Rename if necessary
        if current_file != final_file_path:
            shutil.move(current_file, final_file_path)
            logger.info(f"Renamed file to: {output_file_name}")
        
        if not os.path.exists(final_file_path):
            raise Exception("File not found after renaming")
        
        file_size = os.path.getsize(final_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        self.upload_progress["total_size"] = file_size
        self.upload_progress["status"] = "uploading"
        
        logger.info(f"Uploading file: {output_file_name} ({file_size_mb:.2f} MB)")
        logger.info(f"Send type from task: '{send_type}'")
        
        try:
            logger.info(f"DEBUG - send_type value: '{send_type}' (type: {type(send_type)})")
            logger.info(f"DEBUG - Condition result: {send_type.lower() in ['doc', 'document', 'file']}")
        
            # Prepare caption
            caption = (
                f"`{output_file_name}`\n"
            )
            
            # Check thumbnail
            thumb = thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None
            
            if send_type.lower() in ["doc", "document", "file"]:
                logger.info("Sending as DOCUMENT")
                result = await self.client.send_document(
                    chat_id=user_id,
                    document=final_file_path,
                    thumb=thumb,
                    caption=caption,
                    force_document=True,  # This forces it to be sent as document
                    file_name=output_file_name,
                    progress=self._progress_callback
                )
                logger.info("✅ File sent successfully as document")
            else:
                logger.info("Sending as VIDEO")
                result = await self.client.send_video(
                    chat_id=user_id,
                    video=final_file_path,
                    thumb=thumb,
                    caption=caption,
                    supports_streaming=True,
                    progress=self._progress_callback
                )
                logger.info("✅ File sent successfully as video")
            
            self.upload_progress["status"] = "completed"
            return result
            
        except Exception as e:
            self.upload_progress["status"] = "failed"
            error_msg = f"Upload failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
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
                logger.info(f"Upload progress: {percentage:.1f}%")

    def get_progress(self) -> dict:
        return self.upload_progress.copy()