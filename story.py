#mostly temp
flags = {
    "quest_accepted": False,
    "has_ember": False,
}

def elder_lines():
    if flags["has_ember"]:
        return [
            "* You found it! And it's still warm...",
            "* The Keep shudders. One iron leg lifts, then another. We're moving again!",
            "* (more story to come.)",
        ]
    if flags["quest_accepted"]:
        return ["* The Keep is still silent. Head east to the Hollow Cave.", 
                "* And remember: you can always talk to monsters. Sometimes that's stronger than a sword.",
        ]
    return [
        "* Ah, a new face! Welcome to Cinderwick, little one.",
        "* Our home is the Wandering Keep, a castle that walks on iron legs. It has carried us accross the mountain for a hundred years",
        "* But three nights ago, its fire spirit went quiet. The Keep stopped mid-step. Everyone is... a little nervous.",
        "* The spirit's ember fell into the Hollow Cave to the east. Bring it back, and the Keep will walk again.",
        "* Be careful. The monsters down there aren't evil, just very, very confused.",
        "* Take these coins for supplies. (You received 25 coins.)",
    ]

def shop_lines():
    return [
        "* Yokoso watashi no Smoldering Spoon! Everything here is slightly warm.", 
        "* Prices are fair. Mostly (hehe..). Take a look!"
    ]

def quest_txt():
    if flags["has_ember"]:
        return "Quest: Return the ember to the Elder"
    if flags["quest_accepted"]:
        return "Quest: Find the ember in the Hollow Cave"
    return "Quest: Talk to the Elder"

#name, price, desc
SHOP_STOCK = [
    ("Star-berry Tea", 10, "Restores a little HP."),
    ("Iron Spoon", 20, "A questionable weapon."),
    ("Patchwork Cloak", 30, "Slightly warm armor.")
]