import json
import os
from typing import Dict, Any


class UserSettings:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_folder = "./src/log/db"
        os.makedirs(self.db_folder, exist_ok=True)

        self.storage_path = os.path.join(self.db_folder, f"{self.user_id}.json")

        self.data: Dict[str, Any] = {}
        self.temp_state: Dict[int, str] = {}

        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            self.data = {}

    def _save(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def _get_default_settings(
        self,
        name: str = "",
        username: str = ""
    ) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
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

    def get(self, name: str = "", username: str = "") -> Dict[str, Any]:
        if not self.data:
            self.data = self._get_default_settings(name, username)
            self._save()
        return self.data

    def update(self, key: str, value: Any, name: str = "", username: str = ""):
        self.get(name, username)
        if key in self.data:
            self.data[key] = value
            self._save()

    def update_metadata(
        self,
        title: str = "",
        author: str = "",
        encoder: str = "",
        name: str = "",
        username: str = ""
    ):
        self.get(name, username)

        if "metadata" not in self.data:
            self.data["metadata"] = {}

        if title:
            self.data["metadata"]["title"] = title
        if author:
            self.data["metadata"]["author"] = author
        if encoder:
            self.data["metadata"]["encoder"] = encoder

        self._save()

    def set_thumbnail(self, path: str, name: str = "", username: str = ""):
        self.get(name, username)
        self.data["thumbnail_path"] = path
        self._save()

    def reset(self):
        name = self.data.get("name", "")
        username = self.data.get("username", "")
        self.data = self._get_default_settings(name, username)
        self._save()