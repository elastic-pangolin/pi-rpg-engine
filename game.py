from menu import *
from pathlib import Path

# commands recognized in game.json
class Command:
    EXIT = "Exit" # exists the game
    SAVE = "Save" # saves current save to a file
    LOAD = "Load" # Load save?
    TRANSITION = "Transition" # transition to another screen
    EXCHANGEITEM = "ExchangeItem" # modify the amounts of things in the inventory, one value is added, the other removed
    PERSIST = "Persist" # save a value to a non-item state slot
    NOOP = "Noop" # print details text (optional)

class Game:
    def __init__(self):
        self.state = {
            "inventory": {},
            "misc": {}
        }
        self.items = {}
        self.default_savefile = "saves/auto.json" # TODO: should saves be encoded?

    def create_screens(self, rpg, data: dict):
        if not self.items:
            # read in item descriptors
            self.items = data["items"].copy()
        screenlist = data["screens"]
        lookup = {}
        index = 1 # index 0 is reserved for main menu
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

                    # helper function: "IF func_1 THEN func_2 ELSE func_3"
                    def _cond_call(func_1, func_2, func_3):
                        success = bool(func_1())
                        if success:
                            func_2()
                        else:
                            func_3()
                        return success

                    # parse messages
                    if action["details"].get("message"):
                        text = action["details"].get("message")
                        functions[functionindex].append(lambda t=text: rpg.func_overlay("", t))
                    # parse state-changing functions
                    if action["command"] == Command.EXIT:
                        functions[functionindex].append(rpg.func_reset)
                    # save to default save-file
                    elif action["command"] == Command.SAVE:
                        functions[functionindex].append(self.save_to_file(rpg, self.default_savefile))
                    # load from default save-file
                    elif action["command"] == Command.LOAD:
                        functions[functionindex].append(self.load_from_file(rpg, self.default_savefile))
                    # save non-item information (will not be printed to inventory)
                    elif action["command"] == Command.PERSIST:
                        var_key = action["details"].get("key")
                        var_value = action["details"].get("value")
                        functions[functionindex].append(lambda k=var_key, v=var_value: self.persist(k,v))
                    # Scene transition in the state machine
                    elif action["command"] == Command.TRANSITION:
                        nextname = action["details"].get("nextScreen")
                        functions[functionindex].append(lambda i=lookup[nextname]: rpg.func_advance(i))
                    # exchanging items with the world
                    elif action["command"] == Command.EXCHANGEITEM:
                        # first, try to remove the remove-item (if any) and on success,
                        # add the add-item. on add failure, the transaction of reverted
                        remitemname = action["details"].get("removeItemName")
                        remamount = action["details"].get("removeAmount")
                        remfailmsg = action["details"].get("removeFailureMessage")
                        if not remfailmsg:
                            remfailmsg = f"You do not have enough of {remitemname}"
                        additemname = action["details"].get("addItemName")
                        addamount = action["details"].get("addAmount")
                        addfailmsg = action["details"].get("addFailureMessage")
                        if not addfailmsg:
                            addfailmsg = f"You cannot carry more of {additemname}"
                        functions[functionindex].append(
                            lambda rn=remitemname, ra=remamount, rm=remfailmsg, an=additemname, aa=addamount, am=addfailmsg:
                            _cond_call(
                                lambda: self.remove_inventory(rn,ra),
                                lambda: _cond_call(
                                    lambda: self.add_inventory(an,aa),
                                    lambda: None,
                                    lambda: _cond_call(
                                        lambda: self.add_inventory(rn,ra),
                                        lambda: rpg.func_overlay("", am),
                                        lambda: None
                                    )
                                ),
                                lambda: rpg.func_overlay("", rm)
                            )
                        )
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

        return screens

    # save to a specified file, if any, else open save menu to choose the file
    def save_to_file(self, rpg, filename: str = None):
        if filename:
            # creates the file if it does not exist
            try:
                with open(filename, "w", encoding="utf-8") as save:
                    print(f"Saving game state into file {str(filename)}")
                    save.write(json.dumps(self.state))
            except:
                rpg.func_overlay("", f"Could not save to {str(filename)}", 0.25)
        else:
            # TODO: add buttons to an overlay?
            rpg.func_overlay("", "Save [S] [LB][LB] " + "[LB]".join([f.name for f in Path("saves/").glob("*.json")]), 1)

    def load_from_file(self, rpg, filename: str = None):
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as save:
                    print(f"Loading game state from file {str(filename)}")
                    self.state = json.loads(save.read())
            except:
                rpg.func_overlay(f"Could not load from {str(filename)}")
        else:
            # TODO: add buttons to overlay?
            rpg.func_overlay("", "Load [L] [LB][LB] " + "[LB]".join([f.name for f in Path("saves/").glob("*.json")]), 1)

    def persist(self, key: str, value):
        self.state[key] = value # TODO: write into 'misc' section?

    def _get_iteminfo(self, key: str):
        for entry in self.items:
            if entry["name"] == key:
                return entry
        return None

    def add_inventory(self, key: str, value: int):
        if key == None:
            return True
        itementry = self._get_iteminfo(key)
        if not itementry:
            print(f"Item '{key}' unknown")
            return True
        if not self.state["inventory"].get(key):
            self.state["inventory"][key] = 0
        if self.state["inventory"][key] + value > itementry.get("max",999): # default max is 999
            return False
        if value > 1:
            print(f"Added {value} {itementry.get('displayNamePlural', key)} to your inventory")
        else:
            print(f"Added {value} {itementry.get('displayNameSingular', key)} to your inventory")
        self.state["inventory"][key] += value
        return True

    def remove_inventory(self, key: str, value: int, min_left:int=0):
        if key == None:
            return True
        itementry = self._get_iteminfo(key)
        if not itementry:
            print(f"Item '{key}' unknown")
            return True
        if self.state["inventory"].get(key):
            if self.state["inventory"][key] - value >= min_left:
                self.state["inventory"][key] -= value
                if value > 1:
                    print(f"Removed {value} {itementry.get('displayNamePlural', key)} from your inventory")
                else:
                    print(f"Removed {value} {itementry.get('displayNameSingular', key)} from your inventory")
                return True
        return False

    def list_inventory(self, rpg):
        itemlist = []
        for name, amount in self.state["inventory"].items():
            if amount == 0:
                continue
            itementry = self._get_iteminfo(name)
            if itementry:
                if amount > 1:
                    itemlist.append(f"{amount} {itementry.get('displayNamePlural')}")
                else:
                    itemlist.append(f"{amount} {itementry.get('displayNameSingular')}")
            else:
                itemlist.append(f"{amount} {name}")
        if not itemlist:
            itemlist = ["there is nothing here"]
        rpg.func_overlay("", "Inventory [I] [LB][LB]" + "[LB]".join(itemlist), 0.75)

