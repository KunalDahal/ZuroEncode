from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

def setup_status_handlers(app: Client, task_queue, admin_ids):
    
    @app.on_message(filters.command("status") & filters.private)
    async def status_command(client: Client, message: Message):
        if message.from_user.id not in admin_ids:
            await message.reply_text("❌ You are not authorized to use this command.")
            return
            
        await show_status(client, message, task_queue)

async def show_status(client: Client, message: Message, task_queue):
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
    
    status_text = "**📊 Queue Status**\n\n"
    status_text += f"**Total in queue:** `{len(task_ids)}`\n"
    status_text += f"**Processing:** `{processing_task is not None}`\n\n"
    
    if processing_task:
        elapsed = ""
        if processing_task.get("started_at"):
            started = datetime.fromisoformat(processing_task["started_at"])
            elapsed_seconds = (datetime.utcnow() - started).seconds
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            if hours > 0:
                elapsed = f" ({hours}h {minutes}m)"
            else:
                elapsed = f" ({minutes}m)"
        
        status_text += f"**🔄 Currently Processing:**\n"
        status_text += f"├ ID: `{processing_task['task_id'][:8]}`\n"
        status_text += f"├ File: `{processing_task['output_filename'][:40]}`\n"
        status_text += f"├ Status: `{processing_task['status']}`\n"
        status_text += f"├ Progress: `{processing_task['progress']}%`{elapsed}\n"
        status_text += f"└ Added: `{processing_task['created_at'][:19]}`\n\n"
    else:
        status_text += "**🔄 Currently Processing:** `None`\n\n"
    
    if queued_tasks:
        status_text += f"**⏳ Queued ({len(queued_tasks)}):**\n"
        for i, task in enumerate(queued_tasks, 1):
            status_text += f"{i}. ID: `{task['task_id'][:8]}` | `{task['output_filename'][:30]}`\n"
    else:
        status_text += "**⏳ Queued:** `None`\n"
    
    if processing_task or queued_tasks:
        status_text += f"\n**📈 Total Tasks:** `{len(task_ids)}`"
    
    await message.reply_text(status_text)