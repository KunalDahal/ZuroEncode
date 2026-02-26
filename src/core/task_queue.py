import asyncio
import uuid
from datetime import datetime

class TaskQueue:
    def __init__(self):
        self.queue = []
        self.processing = False
        self.lock = asyncio.Lock()
        self.tasks = {}
        self.current_task = None

    def create_task(self, task_data):
        task_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        task = {
            "task_id": task_id,
            "created_at": now,
            "started_at": None,
            "status": "queued",
            "progress": 0,
        }
        
        task.update(task_data)
        
        self.tasks[task_id] = task
        self.queue.append(task_id)
        
        return task_id

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def update_status(self, task_id, status, progress=None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
            
            if status in ["downloading", "encoding", "uploading"] and not self.tasks[task_id].get("started_at"):
                self.tasks[task_id]["started_at"] = datetime.utcnow().isoformat()

    def remove_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
        if task_id in self.queue:
            self.queue.remove(task_id)
        if self.current_task == task_id:
            self.current_task = None

    def get_next_task(self):
        for task_id in self.queue:
            task = self.tasks.get(task_id)
            if task and task.get("status") == "queued":
                self.current_task = task_id
                return task
        return None

    def get_queue_position(self, task_id):
        try:
            position = 1
            for tid in self.queue:
                task = self.tasks.get(tid)
                if task and task.get("status") in ["queued", "downloading", "encoding", "uploading"]:
                    if tid == task_id:
                        return position
                    position += 1
            return 0
        except:
            return 0

    def is_processing(self):
        return self.processing
    
    def set_processing(self, status):
        self.processing = status

    def get_current_task(self):
        if self.current_task:
            return self.tasks.get(self.current_task)
        return None