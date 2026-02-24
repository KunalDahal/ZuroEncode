import json
import os
from typing import Dict, Any

class UserSettings:
    def __init__(self, storage_path: str = "user_settings.json"):
        self.storage_path = storage_path
        self.data: Dict[int, Dict[str, Any]] = {}
        self.temp_state: Dict[int, str] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.data = json.load(f)
                    self.data = {int(k): v for k, v in self.data.items()}
            except:
                self.data = {}

    def _save(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def _get_default_settings(self, user_id: int, name: str = "", username: str = "") -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "name": name,
            "username": username,
            "resolution": "1080p",
            "crf": 28,
            "preset": "medium",
            "codec": "libx264",
            "audio_bitrate": "128k",
            "metadata": {
                "title": "",
                "author": "",
                "encoder": ""
            },
            "thumbnail_path": ""
        }

    def get(self, user_id: int, name: str = "", username: str = "") -> Dict[str, Any]:
        if user_id not in self.data:
            self.data[user_id] = self._get_default_settings(user_id, name, username)
            self._save()
        return self.data[user_id]

    def update(self, user_id: int, key: str, value: Any, name: str = "", username: str = ""):
        self.get(user_id, name, username)
        if key in self.data[user_id]:
            self.data[user_id][key] = value
            self._save()

    def update_metadata(self, user_id: int, title: str = "", author: str = "", 
                       encoder: str = "", name: str = "", username: str = ""):
        self.get(user_id, name, username)
        if "metadata" not in self.data[user_id]:
            self.data[user_id]["metadata"] = {}
        if title:
            self.data[user_id]["metadata"]["title"] = title
        if author:
            self.data[user_id]["metadata"]["author"] = author
        if encoder:
            self.data[user_id]["metadata"]["encoder"] = encoder
        self._save()

    def set_thumbnail(self, user_id: int, path: str, name: str = "", username: str = ""):
        self.get(user_id, name, username)
        self.data[user_id]["thumbnail_path"] = path
        self._save()

    def reset(self, user_id: int):
        if user_id in self.data:
            name = self.data[user_id].get("name", "")
            username = self.data[user_id].get("username", "")
            self.data[user_id] = self._get_default_settings(user_id, name, username)
            self._save()