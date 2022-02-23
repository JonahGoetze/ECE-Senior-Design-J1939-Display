from abc import ABC, abstractmethod
from multiprocessing import Process, Event
from time import sleep
from queue_manager import QueueManager


class HatAdapter(Process, ABC):
    def __init__(self, queue_manager: QueueManager):
        super(Process, self).__init__()
        super(ABC, self).__init__()
        self.exit = Event()
        self.queue_manager = queue_manager

    def startup_hook(self):
        """
        Override to run some logic at startup
        """
        pass

    def shutdown_hook(self):
        """
        Override to run some logic prior to shutdown
        """
        pass

    @abstractmethod
    def loop(self):
        """The main run loop"""
        pass

    def run(self):
        try:
            self.startup_hook()
            while not self.exit.is_set():
                self.loop()
                sleep(0.1)
            self.shutdown_hook()
        except Exception as e:
            self.log.error("Unhandled exception:", e)
            self.shutdown_hook()



    def stop(self):
        self.exit.set()
