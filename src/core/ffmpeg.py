import asyncio
from typing import Dict, Any, List
import os


class FFmpeg:
    def __init__(self, ffmpeg_path: str = "./src/bin/ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def build_command(self, input_path: str, output_path: str, settings: Dict[str, Any]) -> List[str]:
        cmd = [self.ffmpeg_path, "-i", input_path, "-y"]
        
        # Map all streams
        cmd.extend(["-map", "0"])
        
        # Copy all codecs first, then apply changes
        cmd.extend(["-c", "copy"])
        
        # Video codec - override if specified
        if settings.get("codec"):
            cmd.extend(["-c:v", settings["codec"]])
        
        # Preset
        if settings.get("preset"):
            cmd.extend(["-preset", settings["preset"]])
        
        # CRF (quality)
        if settings.get("crf") is not None:
            cmd.extend(["-crf", str(settings["crf"])])
        
        # Resolution
        if settings.get("resolution"):
            height = settings["resolution"].replace("p", "")
            cmd.extend(["-vf", f"scale=-2:{height}"])
        
        # Audio settings - override if specified
        if settings.get("audio_bitrate"):
            cmd.extend(["-c:a", "aac", "-b:a", settings["audio_bitrate"]])
        
        # Remove all metadata and set custom metadata
        cmd.extend(["-map_metadata", "-1", "-map_chapters", "-1"])
        
        # Add custom metadata from user settings
        metadata = settings.get("metadata", {})
        if metadata.get("title"):
            cmd.extend(["-metadata", f"title={metadata['title']}"])
        if metadata.get("author"):
            cmd.extend(["-metadata", f"artist={metadata['author']}"])
        if metadata.get("encoder"):
            cmd.extend(["-metadata", f"encoder={metadata['encoder']}"])
        
        # Thumbnail (if exists)
        if settings.get("thumbnail_path") and os.path.exists(settings["thumbnail_path"]):
            cmd.extend([
                "-i", settings["thumbnail_path"],
                "-map", "1", "-map", "0",
                "-disposition:v:1", "attached_pic"
            ])
        
        if not output_path.startswith("./src/log/tmp/"):
            filename = os.path.basename(output_path)
            output_path = os.path.join("./src/log/tmp/", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd.append(output_path)
        return cmd

    async def execute(self, cmd: List[str]) -> bool:
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False