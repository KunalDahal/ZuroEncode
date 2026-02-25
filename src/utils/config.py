import os
from typing import List
from dotenv import load_dotenv


class Config:
    
    def __init__(self):
        load_dotenv()
        
        self.session_string: str = os.getenv("SESSION_STRING", "")
        self.api_id: int = int(os.getenv("API_ID", "0"))
        self.api_hash: str = os.getenv("API_HASH", "")
        
        allowed_group_ids_str = os.getenv("ALLOWED_GROUP_IDS", "0")
        self.allowed_group_ids: List[int] = []
        if allowed_group_ids_str:
            try:
                self.allowed_group_ids = [int(x.strip()) for x in allowed_group_ids_str.split(",") if x.strip()]
            except ValueError:
                pass
        
        self.ffmpeg_path: str = os.getenv("FFMPEG_PATH", "./src/bin/ffmpeg")
        self.temp_dir: str = "./src/log/tmp"
        
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids: List[int] = []
        if admin_ids_str:
            try:
                self.admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
            except ValueError:
                pass
        
        self._validate()
    
    def _validate(self):
        if not self.session_string:
            raise ValueError("SESSION_STRING is required")
        if not self.api_id:
            raise ValueError("API_ID is required")
        if not self.api_hash:
            raise ValueError("API_HASH is required")
        if not self.allowed_group_ids or self.allowed_group_ids[0] == 0:
            raise ValueError("ALLOWED_GROUP_IDS is required")