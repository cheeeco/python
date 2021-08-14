import uuid
import threading

from collections import OrderedDict


class Task:
    def __init__(self, length: int, data: bytes):
        self.length = length
        self.data = data
        self.status = 'ENQUEUED'
        self.id = str(uuid.uuid4())


class TaskQueue:
    def __init__(self, q_name: str):
        self.q_name = q_name
        self.tasks = OrderedDict()

    def get_task(self):
        for id, task in list(self.tasks.items()):
            if task.status == 'ENQUEUED':
                task.status = 'PROCESSING'
                timeout_ctrl = threading.Timer(10, self._requeue_task, [id])
                timeout_ctrl.start()
                return str(task.id).encode('utf-8') + b' ' + str(task.length).encode('utf-8') + b' ' + task.data

        return b'NONE'

    def add_task(self, length: int, data: bytes):
        new_task = Task(length, data)
        self.tasks[new_task.id] = new_task
        return new_task.id.encode('utf-8')

    def ack_task(self, id: str):
        if id in self.tasks and self.tasks[id].status == 'PROCESSING':
            del self.tasks[id]
            return b'YES'

        return b'NO'

    def check_task(self, id: str):
        if id in self.tasks:
            return b'YES'
        else:
            return b'NO'

    def _requeue_task(self, id: str):
        if id in self.tasks:
            self.tasks[id].status = 'ENQUEUED'

    def _print(self):
        for id, task in list(self.tasks.items()):
            print('ID: ', id, ';    STATUS: ', task.status, ';', sep='')
        print('\n')
