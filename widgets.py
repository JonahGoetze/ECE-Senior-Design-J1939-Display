import random
import math

from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty
from queue_manager import QueueManager

class TextGague(Widget):
    value = NumericProperty(0)
    note = StringProperty()
    display_value = StringProperty()
    title = StringProperty()
    format_string = StringProperty()

    def set_value(self, value):
        self.value = value

    def set_note(self, n):
        self.note = n
        self.update_display_value()

    def clear_note(self):
        self.note = ""
        self.update_display_value()

    def update_display_value(self):
        if self.note != "":
            self.display_value = self.note
        else:
            self.display_value = (
                f"{self.value:3d}"
                if not isinstance(self.value, float)
                else "{0:5.2f}".format(self.value)
            )

class Gague(Widget):
    max_value = NumericProperty(1)
    value = NumericProperty(0)
    note = StringProperty()
    display_value = StringProperty()
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
        percent = max(min(percent,1.0),0.0)
        self.current_gague_width = math.floor(self.width * percent)

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
        self.update_display_value()

    def set_note(self, n):
        self.note = n
        self.update_display_value()

    def clear_note(self):
        self.note = ""
        self.update_display_value()

    def update_display_value(self):
        if self.note != "":
            self.display_value = f"{self.title}: {self.note}"
        else:
            self.display_value = (
                "{0} {1:5d}".format(self.title, self.value)
                if not isinstance(self.value, float)
                else "{0} {1:5.2f}".format(self.title, self.value)
            )



class Root(Widget):
    gps_speed_gauge = ObjectProperty(None)
    rpm_gauge = ObjectProperty(None)
    temp_gauge = ObjectProperty(None)
    count = 0

    gps_speed = 0
    gps_speed
    rpm = 0
    coolant_temp = 0

    queue_manager = QueueManager.load()

    def update(self, delta):
        """
        Note: Kivy should magically patch in the "self" from "vis.py" which should contain self.queue_manater for access
        to the event queues.
        """
        # Update voltage
        updated_gps_speed = self.queue_manager.gps_speed.get_or_else(self.gps_speed)
        if updated_gps_speed <= -1:
            self.gps_speed = 0
            self.gps_speed_gauge.set_note("GPS")
        elif updated_gps_speed > 3:
            self.gps_speed = updated_gps_speed
            self.gps_speed_gauge.clear_note()
        else:
            self.gps_speed = 0
            self.gps_speed_gauge.clear_note()

        # Update rpm
        self.rpm = self.queue_manager.rpm.get_or_else(self.rpm)

        # update temp
        self.coolant_temp = self.queue_manager.temp.get_or_else(self.coolant_temp)

        self.gps_speed_gauge.set_value(
            0 if isinstance(self.gps_speed, str)  else self.gps_speed
        )
        self.rpm_gauge.set_value(self.rpm)
        self.temp_gauge.set_value(self.coolant_temp)
