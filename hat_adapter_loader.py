import io
from hat_adapter_abc import HatAdapter
from queue_manager import QueueManager


class HatAdapterLoader:
    """
    In order for the rasberry pi to interop with it's hat extensions, it requires use of a few linux and rasberry pi
    specific libraries. This class will detect if the system is running on a rasberry pi, and if not, it will load
    a simulation environment instead of the OS specific libraries which would cause the program to crash.
    """
    def __init__(self):
        pass

    def load(self) -> HatAdapter:
        """
        Detect if the application is running on a rasberry pi. If not, a simulation client is loaded to simulate the
        hat.
        :return: HatAdapter
        """
        qm = QueueManager.load()
        if self._is_raspberry_pi():
            from hat_manager import HatManager
            return HatManager(qm)
        else:
            from hat_simulator import HatSimulator
            return HatSimulator(qm)

    def _is_raspberry_pi(self, raise_on_errors=False) -> bool:
        """Checks if Raspberry PI.
        :return: Boolean indicating if the current system is a rasberry pi.

        Credit to: https://gist.github.com/barseghyanartur/94dbda2ad6f8937d6c307811ad51469a
        """
        try:
            with io.open('/proc/cpuinfo', 'r') as cpuinfo:
                found = False
                for line in cpuinfo:
                    if line.startswith('Hardware'):
                        found = True
                        label, value = line.strip().split(':', 1)
                        value = value.strip()
                        if value not in (
                                'BCM2708',
                                'BCM2709',
                                'BCM2711',
                                'BCM2835',
                                'BCM2836'
                        ):
                            if raise_on_errors:
                                raise ValueError(
                                    'This system does not appear to be a '
                                    'Raspberry Pi.'
                                )
                            else:
                                return False
                if not found:
                    if raise_on_errors:
                        raise ValueError(
                            'Unable to determine if this system is a Raspberry Pi.'
                        )
                    else:
                        return False
        except IOError:
            if raise_on_errors:
                raise ValueError('Unable to open `/proc/cpuinfo`.')
            else:
                return False

        return True