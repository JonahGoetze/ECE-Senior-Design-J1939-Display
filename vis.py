import sys
from queue_manager import QueueManager
from hat_adapter_loader import HatAdapterLoader

test = "--test" in sys.argv
sys.argv = ["test"]

from kivy.app import App
from kivy.clock import Clock
from widgets import Root

from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["debug"])

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullsreen', 0) # set 1 for fullscreen 0 for windowed dev purposes
Config.set('graphics', 'show_cursor', 0)
Config.set('graphics', 'borderless', 0) # change to 1 for final version
Config.set('graphics', 'max_fps', 60)
Config.set('graphics', 'allow_screensaver', 0)
Config.set('kivy', 'show_fps', '1')
Config.set('modules', 'monitor', '') # comment to hide fps
Config.write()

#from gps_reader import GpsReader
#from obdii_reader import ObdiiReader
#from J1939_reader import J1939Reader

class VisApp(App):
    def build(self):
        root = Root()
        Clock.schedule_interval(root.update, 1.0/60.0)

        return root

    def on_start(self):

        self.queue_manager = QueueManager.load()
        loader = HatAdapterLoader()
        self.hat = loader.load()
        self.hat.start()

    def on_stop(self):
        self.hat.stop()

if __name__ == '__main__':
    VisApp().run()
