__version__ = "1.0.0"

from .core import TaskQueue, UserSettings, FFmpeg
from .services import Downloader, Encoder, Uploader, Worker
from .utils import Config, admin_only
from .handlers.encode import setup_encode_handlers
from .handlers.settings import setup_settings_handlers
from src.handlers.status import setup_status_handlers

__all__ = [
    "__version__",
    "TaskQueue", "UserSettings", "FFmpeg",
    "Downloader", "Encoder", "Uploader", "Worker",
    "Config", "admin_only",
    "setup_encode_handlers",
    "setup_settings_handlers",
]