import asyncio
import uuid
from datetime import datetime

class TaskQueue:
    def __init__(self):
        self.queue = []
        self.processing = False
        self.lock = asyncio.Lock()
        self.tasks = {}
        self.worker = None

    def set_worker(self, worker):
        self.worker = worker

    def create_task(self, task_data):
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        task = {
            "task_id": task_id,
            "user_id": task_data["user_id"],
            "chat_id": task_data["chat_id"],
            "file_id": task_data["file_id"],
            "original_file_name": task_data["original_file_name"],
            "output_file_name": task_data["output_filename"],
            "split_size": task_data["split_size"],
            "created_at": now,
            "status": "queued"
        }
        
        self.tasks[task_id] = task
        self.queue.append(task_id)
        
        return task_id

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def update_status(self, task_id, status):
        if task_id in self.tasks and status in ["queued", "downloading", "encoding", "uploading"]:
            self.tasks[task_id]["status"] = status

    def remove_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
        if task_id in self.queue:
            self.queue.remove(task_id)

    def get_next_task(self):
        for task_id in self.queue:
            if self.tasks.get(task_id, {}).get("status") == "queued":
                return self.tasks[task_id]
        return None

    def get_queue_position(self, task_id):
        try:
            position = 1
            for tid in self.queue:
                if tid == task_id:
                    return position
                if self.tasks.get(tid, {}).get("status") == "queued":
                    position += 1
            return 0
        except:
            return 0

    def get_queue_count(self):
        queued_count = 0
        for task_id in self.queue:
            if self.tasks.get(task_id, {}).get("status") == "queued":
                queued_count += 1
        return queued_count

    def is_processing(self):
        return self.processing
    
    def set_processing(self, status):
        self.processing = status