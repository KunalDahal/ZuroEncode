import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from collections import deque


class TaskQueue:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.queue = deque()
        self.processing = False
        self._lock = asyncio.Lock()

    def create_task(self, user_id: int, chat_id: int, file_id: str, 
                   original_filename: str, output_filename: str) -> str:
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        self.tasks[task_id] = {
            "task_id": task_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "file_id": file_id,
            "original_filename": original_filename,
            "output_filename": output_filename,
            "status": None,
            "created_at": now,
            "started_at": None,
        }
        
        self.queue.append(task_id)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def update_status(self, task_id: str, status: str, error: str = None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if error:
                self.tasks[task_id]["error"] = error
            if status in ["downloading", "encoding", "uploading"] and not self.tasks[task_id]["started_at"]:
                self.tasks[task_id]["started_at"] = datetime.utcnow().isoformat()

    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
        if task_id in self.queue:
            self.queue.remove(task_id)

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        while self.queue:
            task_id = self.queue[0]
            task = self.tasks.get(task_id)
            if task and task["status"] == "queued":
                return task
            else:
                self.queue.popleft()
        return None

    def get_queue_position(self, task_id: str) -> int:
        try:
            return list(self.queue).index(task_id) + 1
        except ValueError:
            return 0

    def is_processing(self) -> bool:
        return any(
            task["status"] in ["downloading", "encoding", "uploading"]
            for task in self.tasks.values()
        )

    def get_queued_count(self) -> int:
        return len([t for t in self.queue if self.tasks[t]["status"] == "queued"])

    def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        return [t for t in self.tasks.values() if t["user_id"] == user_id]