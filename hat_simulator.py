from hat_adapter_abc import HatAdapter
import random


class HatSimulator(HatAdapter):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)
        self.voltage = 0
        self.rpm = 0
        self.temp = 0

        self.max_voltage = 16
        self.max_rpm = 4600
        self.max_temp = 250

        self.target_voltage = 0
        self.target_rpm = 0
        self.target_temp = 0


    def loop(self):
        # update speed
        (self.voltage, self.target_voltage) = self._interpolate(self.voltage, self.target_voltage, self.max_voltage, 2)
        self.queue_manager.voltage.put(self.voltage)

        # update rpm
        (self.rpm, self.target_rpm) = self._interpolate(self.rpm, self.target_rpm, self.max_rpm, 40)
        self.queue_manager.rpm.put(self.rpm)

        # update temp
        (self.temp, self.target_temp) = self._interpolate(self.temp, self.target_temp, self.max_temp, 20)
        self.queue_manager.temp.put(self.temp)

    def _interpolate(self, value, target, max_value, step):
        if value == target:
            target = random.randint(0, max_value)
        if value > target:
            if value - step < target:
                value -= 1
            else:
                value -= random.randint(1, step)
        elif value < target:
            if value + step > target:
                value += 1
            else:
                value += random.randint(1, step)
        return (value, target)

