import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    
    def __init__(self):
        load_dotenv()
        
        self.bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.api_id: str = os.getenv("API_ID", "")
        self.api_hash: str = os.getenv("API_HASH", "")
        self.allowed_group_id: int = int(os.getenv("ALLOWED_GROUP_ID", "0"))
        self.settings_file: str = os.getenv("SETTINGS_FILE", "./user_settings.json")
        
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids: list[int] = []
        if admin_ids_str:
            try:
                self.admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
            except ValueError:
                pass
        
        self._validate()
    
    def _validate(self):
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.api_id:
            raise ValueError("API_ID is required")
        if not self.api_hash:
            raise ValueError("API_HASH is required")
        if not self.allowed_group_id:
            raise ValueError("ALLOWED_GROUP_ID is required")