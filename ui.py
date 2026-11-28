import pygame
from settings import *
from items import ITEMS, use_item

class DialogueBox:
    def __init__(self, ft):
        self.ft = ft
        self.active = False
        self.name = ""
        self.lines = []
        self.index = 0
        self.chars = 0.0
    def start(self, name, lines):
        self.name = name
        self.lines = lines
        self.index = 0
        self.chars = 0.0
        self.active = True
    def current(self):
        return self.lines[self.index]
    def done_type(self):
        return int(self.chars) >= len(self.current())
    def advance(self):
        #1st press finish line, 2nd press go next
        if not self.done_type():
            self.chars = len(self.current())
        else:
            self.index += 1
            self.chars = 0.0
            if self.index >= len(self.lines):
                self.active = False
    def update(self, dt):
        if self.active and not self.done_type():
            self.chars += TXT_SPEED * dt
    def wrap(self, txt, max_w):
        words = txt.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = w if not cur else cur + " " +w
            if self.ft.size(test)[0]<=max_w:
                cur =test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines
    def draw(self, surface):
        if not self.active:
            return
        box = pygame.Rect(8, H - 62, W - 16, 54)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill(DIALOGUE_BG)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, DIALOGUE_BORDER, box, 1)
        name = self.ft.render(self.name, False, DIALOGUE_NC)
        surface.blit(name, (box.x + 6, box.y + 4))

        #wrap full line then reveal letter by letter
        wrapd = self.wrap(self.current(), box.width - 12)
        remainin = int(self.chars)
        y = box.y + 18
        for line in wrapd:
            if remainin <= 0:
                break
            part = line[:remainin]
            surface.blit(self.ft.render(part, False, TXT_COLOR), (box.x+6,y))
            remainin -= len(line) + 1
            y += 11
        if self.done_type():
            hint = self.ft.render("[E]", False, DIALOGUE_NC)
            surface.blit(hint, (box.right - hint.get_width() - 6, box.bottom - 12))
class ShopMenu:
    def __init__(self,ft, stock):
        self.ft = ft
        self.stock = stock
        self.cursor = 0
        self.message = ""
    def reset(self):
        self.cursor = 0
        self.message = ""
    def move(self,d):
        self.cursor = (self.cursor + d) % len(self.stock)
        self.message = ""
    def buy(self,player):
        name, price, _ = self.stock[self.cursor]
        if player.coins >= price:
            player.coins -= price
            player.inventory[name] = player.inventory.get(name,0) + 1
            self.message = "Bought " + name + "!"
        else:
            self.message = "Not enough coins..."
    def draw(self,surface,player):
        box = pygame.Rect(W//2 - 130,40,260,130)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill(DIALOGUE_BG)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, DIALOGUE_BORDER, box, 1)

        title = self.ft.render("Smoldering Spoon", False, DIALOGUE_NC)
        surface.blit(title, (box.x + 8, box.y + 6))
        coins = self.ft.render("Coins: " + str(player.coins), False, TXT_COLOR)
        surface.blit(coins, (box.right - coins.get_width() - 8, box.y + 6))

        y = box.y + 26
        for i, (name, price, desc) in enumerate(self.stock):
            color = DIALOGUE_NC if i == self.cursor else TXT_COLOR
            prefix = "> " if i == self.cursor else "  "
            owned = player.inventory.get(name,0)
            surface.blit(self.ft.render(prefix + name, False, color), (box.x + 8, y))
            right = self.ft.render(str(price) + "c  (x" +str(owned) + ")", False, color)
            surface.blit(right, (box.right - right.get_width() - 8,y))
            y+=14
        desc = self.stock[self.cursor][2]
        surface.blit(self.ft.render(desc, False, TXT_COLOR), (box.x + 8, box.bottom - 38))
        if self.message:
            surface.blit(self.ft.render(self.message, False, DIALOGUE_NC), (box.x + 8, box.bottom - 26))
        hint = self.ft.render("W/S move    E buy    Q leave", False, DIALOGUE_BORDER)
        surface.blit(hint, (box.x+8, box.bottom-14))
class InventoryMenu:
    def __init__(self, ft):
        self.ft = ft
        self.cursor = 0
        self.message = ""
    def names(self,player):
        return [n for n in ITEMS if player.inventory.get(n,0)>0]
    def reset(self):
        self.cursor = 0
        self.message = ""
    def move(self,d,player):
        names = self.names(player)
        if names:
            self.cursor(self.cursor+d)% len(names)
        self.message = ""
    def use(self,player):
        names = self.names(player)
        if not names:
            return
        self.cursor = min(self.cursor, len(names) -1)
        used, msg, _ = use_item(player, names[self.cursor])
        self.message = msg
        names = self.names(player)
        self.cursor = min(self.cursor, max(0, len(names)-1))
    def draw(self,surface, player):
        names = self.names(player)
        self.cursor = min(self.cursor, max(0, len(names) -1))
        box = pygame.Rect(W//2 - 150,24,300,210)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill(DIALOGUE_BG)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, DIALOGUE_BORDER, box,1)

        surface.blit(self.ft.render("Inventory", False, DIALOGUE_NC), (box.x + 8, box.y+6))
        coins = self.ft.render("Coins: "+ str(player.coins), False, TXT_COLOR)
        surface.blit(coins, (box.right - coins.get_width() - 8, box.y + 6))

        s = player.stats
        info = ("LV " + str(player.level) + "   HP" +str(s.hp) + "/" + str(s.max_hp) + "    ATK " + str(s.attack) + "   DEF " + str(s.defense))
        surface.blit(self.ft.render(info, False, TXT_COLOR), (box.x +8, box.y + 22))
        y = box.y + 44
        if not names:
            surface.blit(self.ft.render("Your bag is empty.", False, TXT_COLOR),(box.x+8,y))
        for i, name in enumerate(names[:7]):
            sel = i == self.cursor
            color = DIALOGUE_NC if sel else TXT_COLOR
            prefix = "> " if sel else "  "
            surface.blit(self.ft.render(prefix + name, False, color), (box.x+8,y))
            cnt = self.ft.render("x" + str(player.inventory[name]), False, color)
            surface.blit(cnt, (box.right - cnt.get_width() - 8,y))
            y += 14
        if names:
            desc = ITEMS[names[self.cursor]].desc
            surface.blit(self.ft.render(desc, False, TXT_COLOR),(box.x+8, box.bottom -52))
        if self.message:
            surface.blit(self.ft.render(self.message, False, DIALOGUE_NC), (box.x++8, box.bottom-38))
        hint = self.ft.render("W/S move    E use    I/Q close", False, DIALOGUE_BORDER)
        surface.blit(hint, (box.x + 8, box.bottom - 14))