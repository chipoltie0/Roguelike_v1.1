"""
This file is built to handle inventories and their movement

The Inventory class will handle items, extending a list essentially,
allowing items (another object, to be pulled out of the inventory and between inventories
"""
import GamePiece as gp


class Item:
    """
    Base item class, mostly to handle moving items around for inventories
    should be inheirited for specific types of items? most likely
    """
    def __init__(self,name, base_identifier, amount=1,allow_stack=True):
        self.name = name
        self.amount = amount
        self.base_identifier = base_identifier
        self.allow_stack = allow_stack

    def rename(self,name: str):
        """
        rename an item
        :param name: new name for item
        :return: updates item.name
        """
        self.name = name


class Inventory:
    """
    This class will contain a list of items that can be moved
    """
    def __init__(self):
        self.inventory = []

    def get_inventory(self,named=True):
        """
        Returns the list of items in it's inventory
        :param:named: if return should return a list of item objects, or names
        :return: either list of item objects, or list of names of the objects
        """
        # iterate through all items, append to out variable
        out = []
        for item in self.inventory:
            if named:
                value = item.name
            else:
                value = item

            out.append(value)

        return out

    def get_inv_ids(self):
        """
        returns a list of inventory unique id's
        :return: list of unique ids
        """
        out = []
        for item in self.inventory:
            out.append(item.base_identifier)

        return out

    def add_item(self,items: list):
        """
        add item to inventory, stack if possible
        :param items: list of items to add to inventory
        :return: nothing, updates self.inventory
        """
        # get list of id's
        item_ids = self.get_inv_ids()

        for item in items:
            # first check if similar item is in inventory
            if item.base_identifier in item_ids:
                # check for stacking

                # get index of match
                item_index = item_ids.index(item.base_identifier)

                #get item from index
                matched_item = self.inventory[item_index]

                can_stack = matched_item.allow_stack
                if can_stack:
                    # add amount to stack
                    matched_item.amount += item.amount
                    if matched_item.amount <= 0:
                        self.inventory.remove(matched_item)
                # for the case where the id is there, but cannot stack, no item is added


            else:
                # new item, add to inventory and add it's base identifier to the list, if copies
                # will be added to, like multiple
                self.inventory.append(item)
                item_ids.append(item.base_identifier)
                if item.amount <= 0:
                    self.inventory.remove(item)


class Pile(gp.Piece):
    """
    Pile of items gamepiece, will have a location and items contained within it
    """
    def __init__(self,map, point, color, char = '/',inventory=[]):
        """
        init inventory and super init game piece
        :param map: map piece is on
        :param point: tuple where piece is at
        :param color: color of character
        :param char: character to represent pile
        :param inventory: list of Items in the pile
        """
        # create inventory and add items to it
        self.inventory = Inventory()
        self.inventory.add_item(inventory)
        super().__init__(map,point,color=color,char=char)
        # check if inventory is empty
        # if empty, mark as false, otherwise true
        self.is_empty = bool(self.inventory)


def get_test_items():
    """
    build a list of test items
    :return: list of items for testing
    """
    out = []
    out.append(Item('potion','potion_base'))
    out.append(Item('gold','gold',))
    out.append(Item('sword','sword_a',allow_stack=False))
    return out[0],out[1],out[2]


