import random
import math
import queue as Q

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty


class Gague(Widget):
    max_value = NumericProperty(1)
    value = NumericProperty(0)
    current_gague_width = NumericProperty(100)

    threshold_1 = NumericProperty(65)
    threshold_2 = NumericProperty(80)
    threshold_3 = NumericProperty(95)

    threshold_1_color = ListProperty([1,   1, 0, 1])
    threshold_2_color = ListProperty([1, 0.5, 0, 1])
    threshold_3_color = ListProperty([1,   0, 0, 1])

    default_bar_color = ListProperty([0, 1, 0, 1])
    bar_color = ListProperty([0, 1, 0, 1])

    title = StringProperty("Temperature")

    def set_value(self, value):
        self.value = value
        percent = self.value / self.max_value
        self.current_gague_width = math.floor(self.width * percent)

        percent

        if (self.threshold_3 != 0 and
            percent >= (self.threshold_3/self.max_value)):
            self.bar_color = self.threshold_3_color
        elif(self.threshold_2 != 0 and
            percent >= (self.threshold_2/self.max_value)):
            self.bar_color = self.threshold_2_color
        elif(self.threshold_1 != 0 and
            percent >= (self.threshold_1/self.max_value)):
            self.bar_color = self.threshold_1_color
        else:
            self.bar_color = self.default_bar_color



class Root(Widget):
    speed_gague = ObjectProperty(None)
    throttle_gague = ObjectProperty(None)
    rpm_gague = ObjectProperty(None)
    temp_gague = ObjectProperty(None)
    count = 0

    gps_speed = 0
    engine_speed = 0
    rpm = 0
    throttle = 0
    coolant_temp = 0

    def update(self, delta):
        #if self.count < 100:
        #    self.count = min(self.count+1, 100)
        #else:
        #    self.count = max(self.count-random.randint(0, 50), 0)

        try:
            self.gps_speed = self.gps_queue.get_nowait()
            self.gps_speed = self.gps_speed if self.gps_speed > 3 else 0
        except Q.Empty as e:
            pass # don't change speed

        #try:
        #    self.engine_speed, self.rpm, self.throttle, self.coolant_temp = self.obdii_queue.get_nowait()
        #except Q.Empty as e:
        #    pass # don't change speed


        self.speed_gague.set_value(self.gps_speed)
        #self.rpm_gague.set_value(self.rpm)
        #self.throttle_gague.set_value(self.throttle)
        #self.temp_gague.set_value(self.coolant_temp)
