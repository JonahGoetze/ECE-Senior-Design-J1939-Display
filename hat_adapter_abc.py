from abc import ABC, abstractmethod
from multiprocessing import Process, Event
from time import sleep
from queue_manager import QueueManager
import logging


class HatAdapter(Process, ABC):
    def __init__(self, queue_manager: QueueManager):
        super(Process, self).__init__()
        super(ABC, self).__init__()
        self.exit = Event()
        self.queue_manager = queue_manager
        self.log_level = logging.INFO # change to INFO for normal use, DEBUG for testing purposes
        self.log = logging.getLogger("hat_adapter_abc")
        self.log.setLevel(self.log_level)

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
        while not self.exit.is_set():
            try:
                self.startup_hook()
                while not self.exit.is_set():
                    self.loop()
                self.shutdown_hook()
            except Exception as e:
                self.log.exception(f"Unhandled exception: {e}")
                self.shutdown_hook()


    def stop(self):
        self.exit.set()
