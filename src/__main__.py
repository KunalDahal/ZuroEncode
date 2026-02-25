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
        self.ffmpeg = FFmpeg(self.config.ffmpeg_path)
        self.downloader = Downloader(self.config.temp_dir)
        self.encoder = Encoder(self.ffmpeg)
        self.uploader = None
        self.worker = None
        self.app = None

    async def initialize(self):
        self.app = Client(
            name="encode_bot",
            session_string=self.config.session_string,
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            workdir=self.config.temp_dir,
            in_memory=True
        )
        
        await self.app.start()
        
        self.uploader = Uploader(self.app)
        self.worker = Worker(
            self.task_queue,
            UserSettings,
            self.ffmpeg,
            self.app
        )
        
        self.task_queue.set_worker(self.worker)

        setup_encode_handlers(self.app, self.task_queue, UserSettings, 
                             self.downloader, self.encoder, self.uploader, self.ffmpeg)
        setup_settings_handlers(self.app, UserSettings)

        return self.app

    async def start(self):
        await self.initialize()
        
        asyncio.create_task(self.worker.start())
        
        me = await self.app.get_me()
        print(f"Bot started as @{me.username}!")
        print(f"Allowed groups: {self.config.allowed_group_ids}")
        
        # Keep the bot running
        await asyncio.Event().wait()

    async def stop(self):
        if self.worker:
            await self.worker.stop()
        if self.app:
            await self.app.stop()

async def main():
    bot = EncodeBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())