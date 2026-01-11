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
            "inventory": {},
            "misc": {}
        }
        self.items = {}

    def create_screens(self, rpg, data: dict):
        if not self.items:
            # read in item descriptors
            self.items = data["items"].copy()
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
                        functions[functionindex].append(rpg.func_reset)
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
                        functions[functionindex].append(lambda n=itemname, a=amount: self.add_inventory(n,a))
                    elif action["command"] == Command.LOOSEITEM:
                        itemname = action["details"].get("itemName")
                        amount = action["details"].get("amount")
                        failuremessage = action["details"].get("failureMessage")
                        def _cond_call(func_1, func_2):
                            if not bool(func_1()):
                                func_2()
                        functions[functionindex].append( lambda n=itemname, a=amount, m=failuremessage: _cond_call(lambda: self.remove_inventory(n,a), lambda: rpg.func_overlay("", m)) )
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

    def add_inventory(self, key: str, value: int):
        if not self.state["inventory"].get(key):
            self.state["inventory"][key] = 0
        print(f"Added {value} {key}(s) to your inventory")
        self.state["inventory"][key] += value
        return True

    def remove_inventory(self, key: str, value: int, min_left:int=0):
        if self.state["inventory"].get(key):
            if self.state["inventory"][key] - value >= min_left:
                self.state["inventory"][key] -= value
                print(f"Removed {value} {key}(s) from your inventory")
                return True
        return False

    def list_inventory(self, rpg):
        itemlist = []
        for name, amount in self.state["inventory"].items():
            if amount == 0:
                continue
            itementry = None
            for entry in self.items:
                if entry["name"] == name:
                    itementry = entry
                    break
            if itementry:
                if amount > 1:
                    itemlist.append(f"{amount} {itementry.get('displayNamePlural')}")
                else:
                    itemlist.append(f"{amount} {itementry.get('displayNameSingular')}")
            else:
                itemlist.append(f"{amount} {name}")
        rpg.func_overlay("", "Inventory [I] [LB][LB]" + "[LB]".join(itemlist), 0.75)
