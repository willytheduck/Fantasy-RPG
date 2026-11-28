class Item:
    def __init__(self,name,kind,value,price,desc):
        self.name = name
        self.kind = kind 
        self.value = value 
        self.price = price
        self.desc = desc

ITEMS = {
    "Star-berry Tea": Item("Star-berry Tea", "heal", 12,10,"Restores 12 HP."),
    "Iron Spoon": Item("Iron Spoon", "weapon", 2,20,"+2 attack. A questionable weapon."),
    "Patchwork Cloak": Item("Patchwork Cloak", "armor", 1,30, "+1 defense. Slightly warm."),
}

def ownd_of_kind(inventory, kind):
    return [n for n, it in ITEMS.items() if it.kind == kind and inventory.get(n, 0)> 0]
def count_kind(inventory,kind):
    return sum(inventory.get(n,0) for n, it in ITEMS.items() if it.kind == kind)
def use_item(player,name):
    it = ITEMS[name]
    if it.kind == "heal":
        s = player.stats
        if s.hp >= s.max_hp:
            return False, "You're full HP. ",0 
        restored = min(it.value, s.max_hp - s.hp)
        s.heal(restored)
        player.inventory[name] -= 1
        return True, "You drink the " + name + ". Restored " +str(restored) + " HP!", restored
    return False, "You can't use that yet.", 0