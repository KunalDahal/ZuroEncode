import json
import os
from typing import Dict, Any

class UserSettings:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_folder = "./src/bin/users"
        os.makedirs(self.db_folder, exist_ok=True)

        self.storage_path = os.path.join(self.db_folder, f"{self.user_id}.json")

        self.data: Dict[str, Any] = {}
        self.temp_state: Dict[int, Dict] = {}

        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.data = json.load(f)
            except:
                self.data = self._get_default_settings()
        else:
            self.data = self._get_default_settings()
        
        if "metadata" not in self.data:
            self.data["metadata"] = {"title": "", "author": "", "encoder": ""}
        if "send_type" not in self.data:
            self.data["send_type"] = "media"

    def _save(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "resolution": "1080p",
            "crf": 28,
            "preset": "medium",
            "codec": "libx264",
            "audio_bitrate": "128k",
            "send_type": "media",
            "metadata": {
                "title": "",
                "author": "",
                "encoder": ""
            },
            "thumbnail_path": ""
        }

    def get(self) -> Dict[str, Any]:
        return self.data

    def update(self, key: str, value: Any):
        if key in self.data:
            self.data[key] = value
            self._save()

    def update_metadata(self, title: str = None, author: str = None, encoder: str = None):
        if "metadata" not in self.data:
            self.data["metadata"] = {}

        if title is not None:
            self.data["metadata"]["title"] = title
        if author is not None:
            self.data["metadata"]["author"] = author
        if encoder is not None:
            self.data["metadata"]["encoder"] = encoder

        self._save()

    def set_thumbnail(self, path: str):
        self.data["thumbnail_path"] = path
        self._save()

    def reset(self):
        self.data = self._get_default_settings()
        self._save()