from hat_adapter_abc import HatAdapter
from queue_manager import QueueManager


class HatManager(HatAdapter):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)

    def loop(self):
        pass
