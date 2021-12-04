import os
os.environ["KIVY_NO_CONFIG"] = "1"
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 1) # set 1 for fullscreen 0 for windowed dev purposes
Config.set('graphics', 'show_cursor', 0)
Config.set('graphics', 'borderless', 1) # change to 1 for final version
Config.set('graphics', 'allow_screensaver', 0)
#Config.set('modules', 'monitor', 0) # comment to hide fps
#Config.set('modules', '', '') # comment to hide fps
Config.set('kivy','exit_on_escape', 0) # uncomment on windows if killing itself at startup


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


class VisApp(App):
    def build(self):
        root = Root()
        Clock.schedule_interval(root.update, 1.0/10.0) # change if experiencing performance issues

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
