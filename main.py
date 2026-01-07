import os
import sys
import json


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
if not os.path.exists("rainyhearts.ttf"):
    print("Missing font 'rainyhearts'")
    print("Please download it here: https://www.dafont.com/rainyhearts.font")
    sys.exit()
else:
    LabelBase.register(
        name="UI",
        fn_regular="rainyhearts.ttf"   # or whatever font file you chose
    )
from kivy.resources import resource_add_path
resource_add_path(".")

from menu import *
from game import *


# App class
class RPG(App):
    def __init__(self):
        super().__init__()
        self.root = None # the game window object
        self.screens = [None] # things to cycle through displaying
        self.game = None

    # Start series of layouts from game.json file
    def func_play(self):
        #print("Button 'play' clicked")
        self.game = Game()
        game_screens = list()
        filepath = "rpg-engine/test-game.json"
        if os.path.exists(filepath):
            with open(filepath, "r") as gamefile:
                print(f"Loading game from {filepath} ...")
                data = json.load(gamefile)
                game_screens = self.game.create_screens(self, data)
                print(f"Game loaded: {len(game_screens)} screens")

        # TODO: when to load save?

        if not len(game_screens) > 0:
            self.screens = [self.screens[0]] + [None] * 2
            # DEMO: overwrite screens with demo
            demo_intro = MenuLayout("", "DEMO")
            demo_intro.add_animation(lambda: self.func_advance(2), gif="pics/animations/cat-3.gif")
            self.screens[1] = demo_intro
        
            demo_menu = MenuLayout("pics/menus/main.jpg", "DEMO")
            demo_menu.add_button(self.func_exit, text="EXIT DEMO")
            demo_menu.add_button(self.func_reset, text="RETURN TO MAIN MENU")
            self.screens[2] = demo_menu
        else:
            self.screens = [self.screens[0]] + game_screens # game screen indices start at 1 !!!
        
        self.root.show(self.screens[1]) # show first game screen at index 1

    # ============== general functions : ==============
    # exit game
    def func_exit(self):
        #print("Button 'exit' clicked")
        App.get_running_app().stop()

    # reset game state and retun to main menu
    def func_reset(self):
        self.game = None
        self.root.show(self.screens[0]) # 'forget' game and go back to main menu

    def func_advance(self, index: int):
        if index > 0 and not self.game:
            print("WARNING: gamestate not found, this might break the functions!")
        if index >= len(self.screens):
            print("ERROR: index out of range!")
            return
        print(f"Advancing to screen {index}")
        self.root.show(self.screens[index])


    # populate root windows and display generic main menu
    def build(self):
        self.root = ScreenRoot()
        main_menu = MenuLayout("pics/menus/main.jpg", "my game")
        main_menu.add_button(self.func_play, text="play")
        main_menu.add_button(self.func_exit, text="exit")
        self.screens[0] = main_menu # main menu will always be index 0
        self.root.show(main_menu)
        return self.root

if __name__ == '__main__':
    RPG().run()
