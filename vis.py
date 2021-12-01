import sys
from multiprocessing import Queue
test = "--test" in sys.argv
sys.argv = ["test"]

from kivy.app import App
from kivy.clock import Clock
from widgets import Root

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullsreen', 1)
Config.set('graphics', 'show_cursor', 0)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'max_fps', 30)
Config.set('graphics', 'allow_screensaver', 0)
Config.write()

from gps_reader import GpsReader
#from obdii_reader import ObdiiReader



class VisApp(App):
    def build(self):
        root = Root()
        Clock.schedule_interval(root.update, 1.0/20.0)

        return root

    def on_start(self):
        print("Starting GPS Reader.")

        # set up gps reader
        self.gps_queue = Queue(1)
        self.root.gps_queue = self.gps_queue
        self.gps_reader = GpsReader(self.gps_queue, "gps_log.csv", test)
        self.gps_reader.start()

        #self.obdii_queue = Queue(1)
        #self.root.obdii_queue = self.obdii_queue
        #self.obdii_reader = ObdiiReader(self.obdii_queue, "obdii_log.csv", test)
        #self.obdii_reader.start()


    def on_stop(self):
        self.gps_reader.shutdown()
        #self.obdii_reader.shutdown()


if __name__ == '__main__':
    VisApp().run()
