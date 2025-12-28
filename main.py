from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '768')
Config.set('graphics', 'height', '512')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
LabelBase.register(
    name="UI",
    fn_regular="rainyhearts.ttf"   # or whatever font file you chose
)
from kivy.resources import resource_add_path
resource_add_path(".")

from menu import *

# App class
class Bla(App):
    root = None


    # Define your button callbacks
    def func_play(self):
        print("Button 'play' clicked")
        demo_menu = MenuLayout("", "DEMO")
        demo_menu.add_button(self.func_exit, text="EXIT DEMO")
        self.root.show(demo_menu)

    def func_exit(self):
        print("Button 'exit' clicked")
        App.get_running_app().stop()

    def build(self):
        self.root = ScreenRoot()
        main_menu = MenuLayout("pics/menus/main.jpg", "my game")
        main_menu.add_button(self.func_play, text="play")
        main_menu.add_button(self.func_exit, text="exit")
        self.root.show(main_menu)
        return self.root

if __name__ == '__main__':
    Bla().run()
