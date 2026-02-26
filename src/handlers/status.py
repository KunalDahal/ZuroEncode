from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import psutil
import time
import humanize
from math import ceil

BOT_START_TIME = time.time()

def setup_status_handlers(app: Client, task_queue, admin_ids, downloader, encoder, uploader):
    
    @app.on_message(filters.command("status") & filters.private)
    async def status_command(client: Client, message: Message):
        if message.from_user.id not in admin_ids:
            await message.reply_text("❌ You are not authorized to use this command.", parse_mode="html")
            return
        await show_status(client, message, task_queue, page=0)
    
    @app.on_callback_query(filters.regex(r"^status_page:(.+):(.+)$"))
    async def status_callback(client: Client, callback_query: CallbackQuery):
        if callback_query.from_user.id not in admin_ids:
            await callback_query.answer("❌ Unauthorized", show_alert=True)
            return
        
        action, page_str = callback_query.data.split(":")[1:]
        page = int(page_str)
        
        if action == "prev":
            page = max(0, page - 1)
        elif action == "next":
            page = page + 1
        elif action == "refresh":
            pass
        
        await show_status(client, callback_query.message, task_queue, page, is_callback=True)
        await callback_query.answer()

async def show_status(client: Client, message: Message, task_queue, page=0, is_callback=False):
    queued_tasks = []
    processing_task = None
    
    current_task = task_queue.get_current_task()
    if current_task and current_task["status"] in ["downloading", "encoding", "uploading"]:
        processing_task = current_task
    
    task_ids = task_queue.queue
    
    for task_id in task_ids:
        task = task_queue.get_task(task_id)
        if task:
            if processing_task and task["task_id"] == processing_task["task_id"]:
                continue
            if task["status"] in ["queued", "downloading", "encoding", "uploading"]:
                queued_tasks.append(task)
    
    all_active_tasks = []
    if processing_task:
        all_active_tasks.append(processing_task)
    all_active_tasks.extend(queued_tasks)
    
    items_per_page = 5
    total_pages = ceil(len(all_active_tasks) / items_per_page) if all_active_tasks else 1
    page = min(page, total_pages - 1)
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_page_tasks = all_active_tasks[start_idx:end_idx]
    
    status_text = ""
    
    for i, task in enumerate(current_page_tasks, start=start_idx + 1):
        user_info = f"@{task['username']}" if task.get('username') else task.get('first_name', 'Unknown')
        user_id = task['user_id']
        
        elapsed = ""
        if task.get('started_at'):
            started = datetime.fromisoformat(task['started_at'])
            elapsed_seconds = (datetime.utcnow() - started).seconds
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            if hours > 0:
                elapsed = f"{hours}h {minutes}m"
            else:
                elapsed = f"{minutes}m"
        
        status_text += f"<b>Title {i}</b>\n"
        
        if task['status'] == 'encoding':
            status_text += f"┃ Encoding in progress...\n"
            status_text += f"┠ Using CPU for encoding\n"
            status_text += f"┠ Status: <code>{task['status']}</code>\n"
            status_text += f"┠ Speed: N/A | Elapsed: {elapsed}\n"
        else:
            progress_data = get_task_progress(task, downloader, encoder, uploader)
            bar_length = 12
            filled = int(progress_data['percentage'] / 100 * bar_length)
            bar = "■" * filled + "□" * (bar_length - filled)
            
            downloaded_str = humanize.naturalsize(progress_data['downloaded'], binary=True)
            total_str = humanize.naturalsize(progress_data['total_size'], binary=True) if progress_data['total_size'] else "Unknown"
            
            status_text += f"┃ [{bar}] {progress_data['percentage']}%\n"
            status_text += f"┠ Processed: {downloaded_str} of {total_str}\n"
            status_text += f"┠ Status: <code>{task['status']}</code>\n"
            
            if progress_data['speed'] > 0:
                speed_str = humanize.naturalsize(progress_data['speed'], binary=True) + "/s"
                status_text += f"┠ Speed: {speed_str} | Elapsed: {elapsed}\n"
            else:
                status_text += f"┠ Speed: -- | Elapsed: {elapsed}\n"
        
        status_text += f"┠ User: {user_info} | ID: <code>{user_id}</code>\n"
        status_text += f"┖ <code>/cancel_{task['task_id'][:12]}</code>\n"
        
        if i < end_idx:
            status_text += ".\n"
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    uptime_parts = []
    if days > 0:
        uptime_parts.append(f"{days}d")
    if hours > 0:
        uptime_parts.append(f"{hours}h")
    if minutes > 0:
        uptime_parts.append(f"{minutes}m")
    if seconds > 0 and not uptime_parts:
        uptime_parts.append(f"{seconds}s")
    uptime_str = "".join(uptime_parts) if uptime_parts else "0s"
    
    free_disk = humanize.naturalsize(disk.free, binary=True)
    disk_percent = disk.used/disk.total*100
    
    status_text += f"\n<b>⌬ Bot Stats</b>\n"
    status_text += f"┠ Tasks: {len(all_active_tasks)}\n"
    status_text += f"┠ CPU: {cpu_percent}% | F: {free_disk} [{disk_percent:.1f}%]\n"
    status_text += f"┖ RAM: {memory.percent}% | UPTIME: {uptime_str}"
    
    keyboard = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"status_page:prev:{page}"))
    
    nav_buttons.append(InlineKeyboardButton("🔄", callback_data=f"status_page:refresh:{page}"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"status_page:next:{page}"))
    
    keyboard.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if is_callback:
        await message.edit_text(status_text, parse_mode="html", reply_markup=reply_markup)
    else:
        await message.reply_text(status_text, parse_mode="html", reply_markup=reply_markup)

def get_task_progress(task, downloader, encoder, uploader):
    progress = {
        'percentage': task.get('progress', 0),
        'downloaded': 0,
        'total_size': task.get('file_size', 0),
        'speed': 0
    }
    
    if task['status'] == 'downloading':
        dl_progress = downloader.get_progress() if downloader else {}
        progress.update({
            'percentage': dl_progress.get('percentage', 0),
            'downloaded': dl_progress.get('downloaded', 0),
            'total_size': dl_progress.get('total_size', task.get('file_size', 0)),
            'speed': dl_progress.get('speed', 0)
        })
    
    elif task['status'] == 'uploading':
        ul_progress = uploader.get_progress() if uploader else {}
        progress.update({
            'percentage': ul_progress.get('percentage', 0),
            'downloaded': ul_progress.get('uploaded', 0),
            'total_size': ul_progress.get('total_size', task.get('file_size', 0)),
            'speed': ul_progress.get('speed', 0)
        })
    
    return progress