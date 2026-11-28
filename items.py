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
    s = player.stats

    if it.kind == "heal":
        if s.hp >= s.max_hp:
            return False, "You're at full HP.", 0
        restored = min(it.value, s.max_hp - s.hp)
        s.heal(restored)
        player.inventory[name] -= 1
        return True, "You drink the " + name + ". Restored " + str(restored) + " HP!", restored

    if it.kind in ("weapon", "armor"):
        slot = it.kind
        old = player.equipment.get(slot)
        if old == name:
            return False, "You already have the " + name + " equipped.", 0
        if slot == "weapon":
            if old:
                s.attack -= ITEMS[old].value
            s.attack += it.value
            stat = "ATK"
        else:
            if old:
                s.defense -= ITEMS[old].value
            s.defense += it.value
            stat = "DEF"
        player.equipment[slot] = name
        return True, "You equipped the " + name + "! +" + str(it.value) + " " + stat, 0

    return False, "You can't use that.", 0