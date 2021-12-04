
from easy_queue import EasyQueue
from multiprocessing import Queue, Manager
import collections

class QueueManager(collections.UserDict):
    """
    Usage: To create a new queue simple attempt to access a "property" matching the name of the queue you want created.
    Further attempts to access that queue by that name will return the same queue instead of creating a new one.

    e.g.
    ```
        m = QueueManager()
        q1 = m.queue_1
        print(q1 == m.queue_1)
        # true
        q2 = m.queue_2
        print(q1 == q2)
        # false
    ```
    """

    instance = None

    @staticmethod
    def load():
        if QueueManager.instance is None:
            QueueManager.instance = QueueManager()
        return QueueManager.instance

    def __init__(self):
        self.rpm = self._build_queue()
        self.voltage = self._build_queue()
        self.temp = self._build_queue()

    def _build_queue(self):
        return EasyQueue(Queue(10))


