import json
import hashlib
import threading
import time
from queue import Queue

class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.Lock()
        self.task_queue = Queue()
        self.db = {}
        self._load()
        self.start_worker()

    def _load(self):
        try:
            with open(self.filename, 'r') as f:
                self.db = json.load(f)
        except FileNotFoundError:
            self.db = {"users": [], "queue": []}
            self._save()
    def _save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.db, f, indent=4)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password):
        hashed_password = self._hash_password(password)
        self.db["users"][username] = {
            "name": username,
            "email": None,
            "display_name": username,
            "password": hashed_password,
            "favarites": [],
            "role": "default",
            "views": 0,
            "coin":0,
            "unlocked": json.dumps(self.unlocked),
            "description": "" 
        }
        self._save()
    def remove_user(self, username):
        if username in self.db["users"]:
            del self.db["users"][username]
            self._save()
        else:
            raise ValueError(f"User {username} does not exist.")
    def change_data(self, username, field, value):
        if field == "password":
            raise Exception("You cannot change the password directly. Use change_password method.")
        if username in self.db["users"]:
            if field in self.db["users"][username]:
                self.db["users"][username][field] = value
                self._save()
            else:
                raise ValueError(f"Field {field} does not exist for user {username}.")
        else:
            raise ValueError(f"User {username} does not exist.")
    def change_password(self, username, old_password, new_password):
        if username in self.db["users"]:
            if self._hash_password(old_password) != self.db["users"][username]["password"]:
                raise ValueError("Old password is incorrect.")
            self.db["users"][username]["password"] = self._hash_password(new_password)
            self._save()
        else:
            raise ValueError(f"User {username} does not exist.")
    def queue_task(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))

    def authenticate(self, username, password):
        if username in self.db["users"]:
            if self._hash_password(password) == self.db["users"][username]["password"]:
                return True
            else:
                raise False
        else:
            raise ValueError(f"User {username} does not exist.")

    def _worker(self):
        while True:
            func, args, kwargs = self.task_queue.get()
            with self.lock:
                func(*args, **kwargs)
                self._save()
            self.task_queue.task_done()

    def start_worker(self):
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()
