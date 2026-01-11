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
        screens = [None] * (len(screenlist)+1)
        functions = {}
        functionindex = 0
        for screen in screenlist:
            # [LB] are literal linebreaks
            layout = MenuLayout("", screen["header"] + "[LB][LB]" + screen["description"])
            for option in screen["options"]:
                functions[functionindex] = [] # list of function to call for an option
                for action in option["actions"]:
                    # parse messages
                    if action["details"].get("message"):
                        text = action["details"].get("message")
                        functions[functionindex].append(lambda t=text: rpg.func_overlay("", t))
                    # parse state-changing functions
                    if action["command"] == Command.EXIT:
                        ...
                    elif action["command"] == Command.SAVE:
                        ...
                    elif action["command"] == Command.LOAD:
                        ...
                    elif action["command"] == Command.TRANSITION:
                        nextname = action["details"].get("nextScreen")
                        functions[functionindex].append(lambda: rpg.func_advance(lookup[nextname]))
                    elif action["command"] == Command.ADDITEM:
                        itemname = action["details"].get("itemName")
                        amount = action["details"].get("amount")
                        failuremessage = action["details"].get("failureMessage")
                        ...
                    elif action["command"] == Command.LOOSEITEM:
                        ...
                    elif action["command"] == Command.NOOP:
                        ...
                    else:
                        print(f"unknown action {str(action)}")
                    def _call_all(functions_list):
                        counter = 1
                        for f in functions_list:
                            #print(f"FUNCTION_{counter} {f.__name__} {f.__code__.co_names} : {f.__code__.co_freevars} {[c.cell_contents for c in f.__closure__ or []]}")
                            f()
                            counter += 1
                layout.add_button(lambda i=functionindex: _call_all(functions[i]), text=option["text"])
                functionindex += 1
            screens[lookup[screen["name"]]] = layout
        
        return screens[1:] # index 0 is reserved for main menu

    def persist(self, key: str, value):
        self.state[key] = value
