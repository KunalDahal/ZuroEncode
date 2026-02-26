import os
import logging

class Encoder:
    def __init__(self, ffmpeg):
        self.ffmpeg = ffmpeg
        self.encode_progress = {
            "status": "idle",
            "percentage": 0,
            "stage": ""
        }

    async def encode(self, task_data: dict, input_path: str, settings: dict) -> str:
        output_file_name = task_data["output_filename"]
        task_folder = os.path.dirname(input_path)
        output_path = os.path.join(task_folder, output_file_name)
        
        if not os.path.exists(input_path):
            raise Exception(f"Input file not found: {input_path}")
        
        logging.info(f"Starting encoding for {input_path} -> {output_path}")
        
        cmd = self.ffmpeg.build_command(input_path, output_path, settings)
        
        self.encode_progress["status"] = "encoding"
        self.encode_progress["stage"] = "starting"
        
        success, error = await self.ffmpeg.execute(cmd)
        
        if not success:
            self.encode_progress["status"] = "failed"
            error_message = f"Encoding failed: {error}"
            logging.error(error_message)
            raise Exception(error_message)
        
        if not os.path.exists(output_path):
            self.encode_progress["status"] = "failed"
            error_message = "Output file not created after encoding"
            logging.error(error_message)
            raise Exception(error_message)
        
        if os.path.getsize(output_path) == 0:
            self.encode_progress["status"] = "failed"
            error_message = "Output file is empty after encoding"
            logging.error(error_message)
            raise Exception(error_message)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        logging.info(f"Encoding completed successfully. Output size: {file_size:.2f} MB")
        
        self.encode_progress["status"] = "completed"
        
        try:
            if input_path != output_path and os.path.exists(input_path):
                os.remove(input_path)
                logging.info(f"Removed input file: {input_path}")
        except Exception as e:
            logging.warning(f"Failed to remove input file: {e}")
            
        return output_path

    def get_progress(self) -> dict:
        return self.encode_progress.copy()