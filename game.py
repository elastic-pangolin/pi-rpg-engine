from menu import *

# commands recognized in game.json
class Command:
    EXIT = "Exit" # exists the game
    SAVE = "Save" # saves current save to a file
    LOAD = "Load" # Load save?
    TRANSITION = "Transition" # transition to another screen
    ADDITEM = "AddItem" # add something to save inventory
    LOOSEITEM = "LooseItem" # remove something from save inventory
    NOOP = "Noop" # print details text (optional)

class Game:
    def __init__(self):
        self.state = {
            "inventory": [],
            "misc": {}
        }

    def create_screens(self, rpg, data: dict):
        screenlist = data["screens"]
        lookup = {}
        index = 1
        # assign indices to screen names
        for screen in screenlist:
            lookup[screen["name"]] = index
            index += 1
        print(lookup) # TODO DELTE ME
        screens = [None] * (len(screenlist)+1)
        for screen in screenlist:
            # [LB] are literal linebreaks
            layout = MenuLayout("", screen["header"] + "[LB][LB]" + screen["description"])
            for option in screen["options"]:
                button_added = False
                for action in option["actions"]:
                    if action["command"] == Command.TRANSITION:
                        nextname = action["details"].get("nextScreen")
                        layout.add_button(
                            lambda: rpg.func_advance(lookup[nextname]),
                            text=option["text"])
                        button_added = True
                        break
                    else:
                        print(f"unknown action {str(action)}")
                if not button_added:
                    layout.add_button(lambda: None, text=option["text"])
            screens[lookup[screen["name"]]] = layout
        
        return screens[1:] # index 0 is reserved for main menu

    def persist(self, key: str, value):
        self.state[key] = value
