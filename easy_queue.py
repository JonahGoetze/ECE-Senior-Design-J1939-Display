from multiprocessing import Queue
from queue import Empty, Full


class EasyQueue:
    """
    A simple multiprocessing.Queue wrapper.
    """

    def __init__(self, queue):
        self._queue = queue

    def get_or_else(self, default, fast_forward=True):
        """
        Will attempt to read from the queue, if the queue is empty, will return the provided default value.

        :param default: The default value to return
        :param fast_forward: If fast_forward is set to true, will drain the queue, only returning the last item in
            the queue.
        :return: the value extracted from the queue or the default.
        """
        if fast_forward:
            pulled_items = []
            while True:
                try:
                    item = self._queue.get_nowait()
                    pulled_items.append(item)
                except Empty as e:
                    if len(pulled_items) > 0:
                        return pulled_items[-1]
                    else:
                        return default
        else:
            try:
                return self._queue.get_nowait()
            except Empty as e:
                return default

    def put(self, item) -> None:
        """
        Add an item to the queue
        :param item: The item to be added to the queue
        :return: None
        """
        try:
            self._queue.put_nowait(item)
        except Full as e:
            pass  # queue was full
