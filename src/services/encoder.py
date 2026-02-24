from typing import Dict, Any
from src.core.ffmpeg import FFmpeg

class Encoder:
    def __init__(self, ffmpeg: FFmpeg):
        self.ffmpeg = ffmpeg

    async def encode(self, input_path: str, output_path: str, settings: Dict[str, Any]) -> bool:
        cmd = self.ffmpeg.build_command(input_path, output_path, settings)
        return await self.ffmpeg.execute(cmd)