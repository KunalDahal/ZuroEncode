import os

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
        
        base_name = os.path.splitext(output_file_name)[0]
        temp_output_name = f"{base_name}_temp.mp4"
        temp_output_path = os.path.join(task_folder, temp_output_name)
        final_output_path = os.path.join(task_folder, output_file_name)
        
        if not os.path.exists(input_path):
            raise Exception(f"Input file not found: {input_path}")
        
        cmd = self.ffmpeg.build_command(input_path, temp_output_path, settings)
        
        self.encode_progress["status"] = "encoding"
        self.encode_progress["stage"] = "starting"
        
        success, error = await self.ffmpeg.execute(cmd)
        
        if not success:
            self.encode_progress["status"] = "failed"
            raise Exception(f"Encoding failed: {error}")
        
        if not os.path.exists(temp_output_path):
            self.encode_progress["status"] = "failed"
            raise Exception("Output file not created after encoding")
        
        if os.path.getsize(temp_output_path) == 0:
            self.encode_progress["status"] = "failed"
            raise Exception("Output file is empty after encoding")
        
        self.encode_progress["status"] = "completed"
        
        if os.path.exists(final_output_path):
            os.remove(final_output_path)
        os.rename(temp_output_path, final_output_path)
        
        try:
            if input_path != final_output_path and os.path.exists(input_path):
                os.remove(input_path)
        except:
            pass
            
        return final_output_path

    def get_progress(self) -> dict:
        return self.encode_progress.copy()