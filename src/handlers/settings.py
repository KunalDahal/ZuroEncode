from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def setup_settings_handlers(app: Client, user_settings):
    
    @app.on_message(filters.command("us") & filters.private)
    async def us_command(client: Client, message: Message):
        user = message.from_user
        user_id = user.id
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = user.username or ""
        
        settings = user_settings.get(user_id, name, username)
        
        text = (
            f"🎛️ **Your Encoding Settings**\n\n"
            f"**User:** {name} (@{username if username else 'N/A'})\n"
            f"**ID:** `{user_id}`\n\n"
            f"**Video:**\n"
            f"• Resolution: `{settings['resolution']}`\n"
            f"• CRF: `{settings['crf']}`\n"
            f"• Preset: `{settings['preset']}`\n"
            f"• Codec: `{settings['codec']}`\n\n"
            f"**Audio:**\n"
            f"• Bitrate: `{settings['audio_bitrate']}`\n\n"
            f"**Metadata:**\n"
            f"• Title: `{settings['metadata']['title'] or 'None'}`\n"
            f"• Author: `{settings['metadata']['author'] or 'None'}`\n"
            f"• Encoder: `{settings['metadata']['encoder'] or 'None'}`\n\n"
            f"**Thumbnail:** {'✅ Set' if settings['thumbnail_path'] else '❌ Not set'}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📺 Resolution", callback_data="set_resolution"),
             InlineKeyboardButton("🎚️ CRF", callback_data="set_crf")],
            [InlineKeyboardButton("⚡ Preset", callback_data="set_preset"),
             InlineKeyboardButton("🎬 Codec", callback_data="set_codec")],
            [InlineKeyboardButton("🔊 Audio Bit Rate", callback_data="set_audio_bitrate"),
             InlineKeyboardButton("📝 Metadata", callback_data="set_metadata")],
            [InlineKeyboardButton("🖼️ Thumbnail", callback_data="set_thumbnail"),
             InlineKeyboardButton("🔄 Reset", callback_data="reset_settings")]
        ])
        
        await message.reply_text(text, reply_markup=keyboard)

    @app.on_callback_query()
    async def handle_callbacks(client: Client, callback_query: CallbackQuery):
        user = callback_query.from_user
        user_id = user.id
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = user.username or ""
        data = callback_query.data

        if data == "set_resolution":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("1080p", callback_data="res_1080p"),
                 InlineKeyboardButton("720p", callback_data="res_720p")],
                [InlineKeyboardButton("480p", callback_data="res_480p"),
                 InlineKeyboardButton("360p", callback_data="res_360p")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_menu")]
            ])
            await callback_query.message.edit_text(
                "Select resolution:",
                reply_markup=keyboard
            )

        elif data.startswith("res_"):
            resolution = data.replace("res_", "")
            user_settings.update(user_id, "resolution", resolution, name, username)
            await callback_query.answer(f"Resolution set to {resolution}")
            await us_command(client, callback_query.message)

        elif data == "set_crf":
            await callback_query.message.edit_text(
                "Send CRF value (0-58):\nLower = better quality, higher = smaller file"
            )
            user_settings.temp_state[user_id] = "waiting_crf"

        elif data == "set_preset":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("ultrafast", callback_data="preset_ultrafast"),
                 InlineKeyboardButton("superfast", callback_data="preset_superfast")],
                [InlineKeyboardButton("veryfast", callback_data="preset_veryfast"),
                 InlineKeyboardButton("faster", callback_data="preset_faster")],
                [InlineKeyboardButton("fast", callback_data="preset_fast"),
                 InlineKeyboardButton("medium", callback_data="preset_medium")],
                [InlineKeyboardButton("slow", callback_data="preset_slow"),
                 InlineKeyboardButton("slower", callback_data="preset_slower")],
                [InlineKeyboardButton("veryslow", callback_data="preset_veryslow")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_menu")]
            ])
            await callback_query.message.edit_text(
                "Select preset:",
                reply_markup=keyboard
            )

        elif data.startswith("preset_"):
            preset = data.replace("preset_", "")
            user_settings.update(user_id, "preset", preset, name, username)
            await callback_query.answer(f"Preset set to {preset}")
            await us_command(client, callback_query.message)

        elif data == "set_codec":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("H.264 (libx264)", callback_data="codec_libx264"),
                 InlineKeyboardButton("H.265 (libx265)", callback_data="codec_libx265")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_menu")]
            ])
            await callback_query.message.edit_text(
                "Select codec:",
                reply_markup=keyboard
            )

        elif data.startswith("codec_"):
            codec = data.replace("codec_", "")
            user_settings.update(user_id, "codec", codec, name, username)
            await callback_query.answer(f"Codec set to {codec}")
            await us_command(client, callback_query.message)

        elif data == "set_audio_bitrate":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("128k", callback_data="abit_128k"),
                 InlineKeyboardButton("192k", callback_data="abit_192k")],
                [InlineKeyboardButton("256k", callback_data="abit_256k"),
                 InlineKeyboardButton("320k", callback_data="abit_320k")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_menu")]
            ])
            await callback_query.message.edit_text(
                "Select audio bitrate:",
                reply_markup=keyboard
            )

        elif data.startswith("abit_"):
            bitrate = data.replace("abit_", "")
            user_settings.update(user_id, "audio_bitrate", bitrate, name, username)
            await callback_query.answer(f"Audio bitrate set to {bitrate}")
            await us_command(client, callback_query.message)

        elif data == "set_metadata":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Set Title", callback_data="meta_title"),
                 InlineKeyboardButton("Set Author", callback_data="meta_author")],
                [InlineKeyboardButton("Set Encoder", callback_data="meta_encoder"),
                 InlineKeyboardButton("Clear All", callback_data="meta_clear")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_menu")]
            ])
            await callback_query.message.edit_text(
                "Metadata options:",
                reply_markup=keyboard
            )

        elif data == "meta_title":
            await callback_query.message.edit_text("Send the title for your videos:")
            user_settings.temp_state[user_id] = "waiting_meta_title"

        elif data == "meta_author":
            await callback_query.message.edit_text("Send the author name:")
            user_settings.temp_state[user_id] = "waiting_meta_author"

        elif data == "meta_encoder":
            await callback_query.message.edit_text("Send the encoder name:")
            user_settings.temp_state[user_id] = "waiting_meta_encoder"

        elif data == "meta_clear":
            user_settings.update_metadata(user_id, "", "", "", name, username)
            await callback_query.answer("Metadata cleared")
            await us_command(client, callback_query.message)

        elif data == "set_thumbnail":
            await callback_query.message.edit_text(
                "Send me an image to use as thumbnail.\nSend /skip to keep current."
            )
            user_settings.temp_state[user_id] = "waiting_thumbnail"

        elif data == "reset_settings":
            user_settings.reset(user_id)
            await callback_query.answer("Settings reset to defaults!")
            await us_command(client, callback_query.message)

        elif data == "back_to_menu":
            await us_command(client, callback_query.message)

    @app.on_message(filters.text & filters.private)
    async def handle_text_input(client: Client, message: Message):
        user_id = message.from_user.id
        name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or ""
        
        if user_id in user_settings.temp_state:
            state = user_settings.temp_state[user_id]
            
            if state == "waiting_crf":
                try:
                    crf = int(message.text)
                    if 0 <= crf <= 58:
                        user_settings.update(user_id, "crf", crf, name, username)
                        del user_settings.temp_state[user_id]
                        await message.reply_text(f"✅ CRF set to {crf}")
                        await us_command(client, message)
                    else:
                        await message.reply_text("❌ CRF must be between 0 and 58")
                except ValueError:
                    await message.reply_text("❌ Please send a valid number")
                    
            elif state == "waiting_meta_title":
                user_settings.update_metadata(user_id, title=message.text, name=name, username=username)
                del user_settings.temp_state[user_id]
                await message.reply_text(f"✅ Title set to: {message.text}")
                await us_command(client, message)
                
            elif state == "waiting_meta_author":
                user_settings.update_metadata(user_id, author=message.text, name=name, username=username)
                del user_settings.temp_state[user_id]
                await message.reply_text(f"✅ Author set to: {message.text}")
                await us_command(client, message)
                
            elif state == "waiting_meta_encoder":
                user_settings.update_metadata(user_id, encoder=message.text, name=name, username=username)
                del user_settings.temp_state[user_id]
                await message.reply_text(f"✅ Encoder set to: {message.text}")
                await us_command(client, message)

    @app.on_message(filters.command("skip") & filters.private)
    async def skip_command(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id in user_settings.temp_state:
            del user_settings.temp_state[user_id]
        await message.reply_text("Skipped.")
        await us_command(client, message)

    @app.on_message(filters.photo & filters.private)
    async def handle_thumbnail(client: Client, message: Message):
        user_id = message.from_user.id
        name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or ""
        
        if user_id in user_settings.temp_state and user_settings.temp_state[user_id] == "waiting_thumbnail":
            file_path = await message.download(file_name=f"thumb_{user_id}.jpg")
            user_settings.set_thumbnail(user_id, file_path, name, username)
            del user_settings.temp_state[user_id]
            await message.reply_text("✅ Thumbnail set!")
            await us_command(client, message)