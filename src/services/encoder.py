import os
from typing import Dict, Any
from src.core.ffmpeg import FFmpeg

class Encoder:
    def __init__(self, ffmpeg: FFmpeg):
        self.ffmpeg = ffmpeg

    async def encode(self, input_dir: str, task_id: str, original_file_name: str, output_file_name: str, settings: Dict[str, Any]) -> str:
        input_path = os.path.join(input_dir, original_file_name)
        output_path = os.path.join(input_dir, output_file_name)
        
        cmd = self.ffmpeg.build_command(input_path, output_path, settings)
        success = await self.ffmpeg.execute(cmd)
        
        if not success:
            raise Exception("Encoding failed")
            
        return output_path