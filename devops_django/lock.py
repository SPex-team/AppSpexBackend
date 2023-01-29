
import time
from . import models as l_models


class DistLock:

    def __init__(self, key: str, valid_time: int):
        self.key = key
        self.valid_time = valid_time

    def _delete_overdue(self):
        now = time.time()
        overdue = now - self.valid_time
        l_models.Lock.objects.filter(key=self.key, timestamp__lte=overdue).delete()

    def acquire(self, timeout=30) -> bool:
        self._delete_overdue()
        start_time = time.time()
        while True:
            now = time.time()
            if now - start_time > timeout:
                return False
            try:
                l_models.Lock.objects.create(key=self.key, timestamp=now)
                return True
            except Exception as exc:
                pass
            time.sleep(0.1)
        return False

    def release(self):
        l_models.Lock.objects.filter(key=self.key).delete()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
