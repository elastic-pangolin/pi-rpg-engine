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
    CONDITION = "Condition"
    NOOP = "Noop" # print details text (optional)

# additional checks and calculations running on persist connands
class Condition:
    LARGER = "larger"
    SMALLER = "smaller"
    EQUAL = "equal"
    UNEQUAL = "unequal"
    # TODO: 

class Persist:
    ADD = "add" # addition/substraction
    MULTIPLY = "multiply"
    SET = "set"


class Game:

    class ExchangeStatus:
        SUCCESS = 1
        ADD_FAIL = 2
        REM_FAIL = 3

    def __init__(self, rpg: RPG):
        self.state = {
            "inventory": {},
            "misc": {}
        }
        self.items = {}
        self.default_savefile = "saves/auto.json" # TODO: should saves be encoded?
        self.rpg = rpg

    def _get_iteminfo(self, key: str):
        for entry in self.items:
            if entry["name"] == key:
                return entry
        return None

    def create_screens(self, data: dict):
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

                def _perform_actions(game: Game, actions_list: list[dict] = []):
                    for action in actions_list:
                        if not action.get("details") or not action.get("command"):
                            continue

                        details = action["details"]
                        command = action["command"]

                        if details.get("message"): # always print the message
                            game.rpg.func_overlay("", action["details"].get("message"))

                        if command == Command.EXIT: # save to default save-file
                            game.rpg.func_reset()
                        elif command == Command.SAVE:
                            game.save_to_file(game.default_savefile)
                        elif command == Command.LOAD: # load from default save-file
                            game.load_from_file(game.default_savefile)
                        elif command == Command.PERSIST: # save non-item information (will not be printed to inventory)
                            game.persist(
                                details.get("formula"),
                                details.get("key"),
                                details.get("value")
                            )
                        elif command == Command.CONDITION:
                            status = game.evaluate(
                                details.get("formula"),
                                details.get("key"),
                                details.get("value")
                            )
                            if status == False:
                                msg = details.get("failureMessage") or f"This is not possible at the moment"
                                game.rpg.func_overlay("", msg)
                                break
                        elif command == Command.TRANSITION: # Scene transition in the state machine
                            game.rpg.func_advance(lookup[action["details"].get("nextScreen")])
                        elif command == Command.EXCHANGEITEM: # exchanging items with the world
                            status = game.exchange_inventory(
                                details.get("addItemName"),
                                details.get("addAmount"),
                                details.get("removeItemName"),
                                details.get("removeAmount")
                            )
                            if status == game.ExchangeStatus.REM_FAIL:
                                msg = details.get("removeFailureMessage") or f"You do not have enough of {details.get("removeItemName")}"
                                game.rpg.func_overlay("", msg)
                            elif status == game.ExchangeStatus.ADD_FAIL:
                                msg = details.get("addFailureMessage") or f"You cannot carry more of {details.get("addItemName")}"
                                game.rpg.func_overlay("", msg)
                        elif action["command"] == Command.NOOP:
                            ...
                        else:
                            print(f"unknown action {str(action)}")

                functions[functionindex].append(lambda g=self, a=option.get("actions"): _perform_actions(g, a))

                layout.add_button(
                    lambda f=functions, i=functionindex: [x() for x in f[i]],
                    text=option["text"]
                )
                functionindex += 1
            screens[lookup[screen["name"]]] = layout

        return screens

    # save to a specified file, if any, else open save menu to choose the file
    def save_to_file(self, filename: str = None):
        if filename:
            # creates the file if it does not exist
            try:
                with open(filename, "w", encoding="utf-8") as save:
                    print(f"Saving game state into file {str(filename)}")
                    save.write(json.dumps(self.state))
            except:
                self.rpg.func_overlay("", f"Could not save to {str(filename)}", 0.25)
        else:
            # TODO: add buttons to an overlay?
            self.rpg.func_overlay("", "Save [S] [LB][LB] " + "[LB]".join([f.name for f in Path("saves/").glob("*.json")]), 1)

    def load_from_file(self, filename: str = None):
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as save:
                    print(f"Loading game state from file {str(filename)}")
                    self.state = json.loads(save.read())
            except:
                self.rpg.func_overlay(f"Could not load from {str(filename)}")
        else:
            # TODO: add buttons to overlay?
            self.rpg.func_overlay("", "Load [L] [LB][LB] " + "[LB]".join([f.name for f in Path("saves/").glob("*.json")]), 1)

    def persist(self, mode: Persist, key: str, value):
        if mode == Persist.ADD:
            if self.state.get(key) is None:
                self.state[key] = 0
            self.state[key] += value
        if mode == Persist.MULTIPLY:
            if self.state.get(key) is None:
                self.state[key] = 1
            self.state[key] *= value
        if mode == Persist.SET:
            self.state[key] = value

    def evaluate(self, condition: Condition, key: str, value) -> bool:
        if condition == Condition.LARGER and not (self.state.get(key) or value) > value:
            return False
        if condition == Condition.SMALLER and not (self.state.get(key) or value) < value:
            return False
        if condition == Condition.EQUAL and not self.state.get(key) == value:
            return False
        if condition == Condition.UNEQUAL and not self.state.get(key) != value:
            return False
        return True

    def exchange_inventory(self, key_add: str, value_add: int, key_rem: str, value_rem: int, min_left: int = None, max_owned: int = None) -> Game.ExchangeStatus:

        # unknown non-none item removed
        if key_rem is not None and self._get_iteminfo(key_rem) is None:
            print(f"Item '{key_rem}' unknown")
            return self.ExchangeStatus.SUCCESS
        # unknwon non-noen item added
        if key_add is not None and self._get_iteminfo(key_add) is None:
            print(f"Item '{key_add}' unknown")
            return self.ExchangeStatus.SUCCESS
        itementry_rem = None
        itementry_add = None
        # check if removal is possible
        removable = True
        if key_rem is not None and value_rem is not None:
            itementry_rem = self._get_iteminfo(key_rem)
            if min_left is None:
                min_left = itementry_rem.get("min") or 0
            itemamount = self.state["inventory"].get(key_rem)
            if itemamount is None or itemamount - value_rem < min_left:
                removable = False
        # check if addition is possible
        addable = True
        if key_add is not None and value_add is not None:
            itementry_add = self._get_iteminfo(key_add)
            if max_owned is None:
                max_owned = itementry_add.get("max") or 999
            itemamount = self.state["inventory"].get(key_add)
            if itemamount is not None and itemamount + value_add > max_owned:
                addable = False
        # apply transaction
        if removable and addable:

            def _transaction_message(mode: str, itementry = {}, value = None):
                if mode == "ADD":
                    formatstr = "Added {} {} to the inventory, now you have {}"
                else:
                    formatstr = "Removed {} {} from the inventory, now you have {}"
                owned = self.state["inventory"].get(itementry.get("name"))
                if value is None:
                    return
                if value > 1:
                    print(formatstr.format(value, itementry.get('displayNamePlural'), owned))
                else:
                    print(formatstr.format(value, itementry.get('displayNameSingular'), owned))

            if key_rem is not None:
                if self.state["inventory"].get(key_rem) is None:
                    self.state["inventory"][key_rem] = 0
                self.state["inventory"][key_rem] -= (value_rem or 0)
                _transaction_message("REM", itementry_rem, value_rem)
            if key_add is not None:
                if self.state["inventory"].get(key_add) is None:
                    self.state["inventory"][key_add] = 0
                self.state["inventory"][key_add] += (value_add or 0)
                _transaction_message("ADD", itementry_add, value_add)
            return self.ExchangeStatus.SUCCESS
        elif not removable:
            return self.ExchangeStatus.REM_FAIL
        else:
            return self.ExchangeStatus.ADD_FAIL

    def list_inventory(self):
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
        self.rpg.func_overlay("", "Inventory [I] [LB][LB]" + "[LB]".join(itemlist), 0.75)

