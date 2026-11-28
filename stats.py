class Stats:
    def __init__(self, name, max_hp, attack, defense, xp=0, coins=0):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.xp_reward = xp #when enemy killd
        self.coin_reward = coins
        self.intro = "" #message when the fight starts (enemy)
        self.hit_txt = "attacks" # how the enemy atk 
    def is_alive(self):
        return self.hp > 0 
    def take_dmg(self,amount):
        self.hp = max(0,self.hp - amount)
    def heal(self,amount):
        self.hp = min(self.max_hp, self.hp + amount)

# placeholder
ENEMY_TYPE = {
    "Glowmoth": {"hp": 12, "attack": 4, "defense":0, "xp":5, "coins":3, "color": (240,200,80), "intro": "* Glowmoth flutters in circles, lighting up the cave.", "hit": "bumps into you with a flash"},
    "Mossling": {"hp": 20, "attack": 5, "defense": 2, "xp": 8, "coins": 5, "color":(90,150,90), "intro": "* Mossling is very confused. It thinks you are a rock.", "hit": "rolls over you"},
    "Dusty Knight": {"hp": 28, "attack": 7, "defense": 2, "xp": 8, "coins": 9, "color": (150,150,170), "intro": "* Dusty Knight clanks forward. It forgot what it was guarding.", "hit": "swings a rusty sword"},
}

def make_enemy_stats(kind):
    d = ENEMY_TYPE[kind]
    s = Stats(kind, d["hp"], d["attack"], d["defense"], d["xp"], d["coins"])
    s.intro = d["intro"]
    s.hit_txt = d["hit"]
    return s