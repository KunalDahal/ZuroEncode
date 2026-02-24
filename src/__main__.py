import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv

from src import (
    TaskQueue,
    UserSettings,
    FFmpeg,
    Downloader,
    Encoder,
    Uploader,
    Worker,
    Config,
    setup_encode_handlers,
    setup_settings_handlers,
)

load_dotenv()

class EncodeBot:
    def __init__(self):
        self.config = Config()
        self.task_queue = TaskQueue()
        self.user_settings = UserSettings(self.config.settings_file)
        self.ffmpeg = FFmpeg(self.config.ffmpeg_path)
        self.downloader = Downloader(self.config.temp_dir)
        self.encoder = Encoder(self.ffmpeg)
        self.uploader = None
        self.worker = None
        self.app = None

    async def initialize(self):
        self.app = Client(
            "encode_bot",
            bot_token=self.config.bot_token,
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            workdir=self.config.temp_dir
        )
        
        self.uploader = Uploader(self.app)
        self.worker = Worker(
            self.task_queue,
            self.user_settings,
            self.ffmpeg,
            self.app,
            self.config.temp_dir
        )

        setup_encode_handlers(self.app, self.task_queue, self.user_settings, 
                             self.downloader, self.encoder, self.uploader, self.ffmpeg)
        setup_settings_handlers(self.app, self.user_settings)

        return self.app

    async def start(self):
        await self.initialize()
        
        asyncio.create_task(self.worker.start())
        
        print(f"Bot started! Allowed group: {self.config.allowed_group_id}")
        await self.app.run()

async def main():
    bot = EncodeBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())