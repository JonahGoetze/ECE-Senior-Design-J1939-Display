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

class VisApp(App):
    def build(self):
        root = Root()
        Clock.schedule_interval(root.update, 1.0/20.0)

        return root

if __name__ == '__main__':
    VisApp().run()
