from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '768')
Config.set('graphics', 'height', '512')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window


from menu import *

# Define your button callbacks
def func_play():
    print("Button 'play' clicked")

def func_exit():
    print("Button 'exit' clicked")
    App.get_running_app().stop()

# App class
class MyApp(App):
    def build(self):
        main_menu = MenuLayout("pics/menus/main.jpg")
        main_menu.add_button(func_play, text="play")
        main_menu.add_button(func_exit, text="exit")
        return main_menu

if __name__ == '__main__':
    MyApp().run()
