import math
import random
import pygame
from settings import *
from items import ITEMS, ownd_of_kind, count_kind
from items import ITEMS, ownd_of_kind, count_kind, use_item

def wrap_txt(ft, txt, max_w):
    words = txt.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = w if not cur else cur + " " +w
        if ft.size(test)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines
def draw_bar(surface,x,y,w,h,value,max_value, color):
    pygame.draw.rect(surface, (60,20,20), (x,y,w,h))
    fill = int(w*max(0,value)/max_value)
    if fill > 0:
        pygame.draw.rect(surface,color,(x,y,fill,h))
    pygame.draw.rect(surface, DIALOGUE_BORDER, (x,y,w,h),1)
def approach(cur, target, step):
    if cur < target:
        return min(target, cur + step)
    return max(target, cur - step)
class Popup:
    def __init__(self,txt,x,y,color,life=0.9):
        self.txt = txt
        self.x = x
        self.y = float(y)
        self.color = color
        self.life = life
    def update(self,dt):
        self.life -= dt
        self.y -=24 * dt
    def draw(self,surface,ft):
        if self.life < 0.2 and int(self.life*20) %2==0:
            return
        img = ft.render(self.txt, False, self.color)
        shadow = ft.render(self.txt, False, (0,0,0))
        x = int(self.x - img.get_width()//2)
        y = int(self.y)
        surface.blit(shadow, (x+1, y+1))
        surface.blit(img, (x,y))
class Battle:
    def __init__(self,ft,player,enemy,enemy_sprite):
        self.ft = ft
        self.big = pygame.font.Font(None, 24)
        self.player = player
        self.hero = player.stats
        self.enemy = enemy
        self.sprite = pygame.transform.scale(enemy_sprite, (48,48))
        self.options = ["Attack", "Item", "Run"]
        self.cursor = 0
        self.phase = "intro"
        self.message = enemy.intro if enemy.intro else "* " + enemy.name + " blocks the way!"
        self.shake = 0.0
        self.popups = []
        self.enemy_hp_shown = float(enemy.hp)
        self.hero_hp_shown = float(self.hero.hp)
        self.result = None #"win", "lose" or "flee" when the battle is over

    def damage(self, attacker, defender):
        #returns
        base = max(1, attacker.attack - defender.defense)
        dmg = max(1, base + random.randint (-DMG_VARIANCE, DMG_VARIANCE))
        crit = random.random() < CRIT_CHANCE
        if crit:
            dmg = max(dmg+1, int(dmg*CRIT_MULT))
        return dmg, crit

    def to_menu(self):
        self.message = "* What will you do?"
        self.phase = "menu"

    def handle_key(self, key):
        confirm = key in (pygame.K_e, pygame.K_RETURN)
        if self.phase  == "menu":
            if key in (pygame.K_a, pygame.K_LEFT):
                self.cursor = (self.cursor - 1)%len(self.options)
            elif key in (pygame.K_d, pygame.K_RIGHT):
                self.cursor = (self.cursor + 1) %len(self.options)
            elif confirm:
                self.choose(self.options[self.cursor])
        elif confirm:
            self.advance()
    def choose(self,option):
        if option == "Attack":
            dmg, crit = self.damage(self.hero, self.enemy)
            self.enemy.take_dmg(dmg)
            self.shake = 0.3
            self.message = "* You strike " + self.enemy.name + " for " + str(dmg) + " damage!"
            if crit:
                self.message += " CRITICAL HIT!!!"
            color = (255,215,100) if crit else (255,255,255)
            self.popups.append(Popup("-" + str(dmg) +("!" if crit else ""), W//2, 40, color))
            self.phase = "player_msg"
        elif option == "Item":
            usable = ownd_of_kind(self.player.inventory, "heal")
            if not usable:
                self.message = "* You have no usable items."
                self.phase = "notice" #turn no use
            else:
                used, msg, amount = use_item(self.player, usable[0])
                self.message = "* " + msg
                if used:
                    self.popups.append(Popup("+" +str(amount), 88,196,(120,230,140)))
                    self.phase = "player_msg" #turn used
                else:
                    self.phase = "notice" #turn no use
        elif option == "Run":
            self.message = "* You fleed."
            self.phase = "flee_msg"
    def advance(self):
        name = self.enemy.name
        if self.phase in ("intro", "notice"):
            self.to_menu()
        elif self.phase == "player_msg":
            if not self.enemy.is_alive():
                xp = self.enemy.xp_reward
                coins = self.enemy.coin_reward
                self.player.coins += coins
                gain = self.player.gain_xp(xp)
                self.message = ("* " +name+" was defeated! You gain " + str(xp) +" XP and "+str(coins)+ " coins.")
                if gain["levels"] >0:
                    txt = "+" + str(gain["hp"]) + " HP, +" + str(gain["atk"]) +" ATK"
                    if gain["def"] >0:
                        txt += ", +" + str(gain["def"]) + " DEF"
                    self.message += " LEVEL UP! You are now LV " + str(self.player.level) + "! (" + txt + ")"
                self.phase = "win_msg"
            else:
                dmg, crit = self.damage(self.enemy, self.hero)
                self.hero.take_dmg(dmg)
                self.message = "* " +name+" "+self.enemy.hit_txt +"! You take " +str(dmg) +" damage"
                if crit:
                    self.message += " Ouuu shiii, a critical hit!"
                self.popups.append(Popup("-" + str(dmg) +("!" if crit else ""), 88, 196, (255,90,90)))
                self.phase = "enemy_msg"
        elif self.phase == "enemy_msg":
            if not self.hero.is_alive():
                self.message = "* You collapsed... The villagers carry you home."
                self.phase = "lose_msg"
            else:
                self.to_menu()
        elif self.phase == "win_msg":
            self.result = "win"
        elif self.phase == "lose_msg":
            self.result = "lose"
        elif self.phase == "flee_msg":
            self.result = "flee"
    def update(self, dt):
        if self.shake > 0:
            self.shake -= dt
        self.enemy_hp_shown = approach(self.enemy_hp_shown, self.enemy.hp,30*dt)
        self.hero_hp_shown = approach(self.hero_hp_shown, self.hero.hp,30*dt)
        for p in self.popups:
            p.update(dt)
        self.popups = [p for p in self.popups if p.life > 0]
    def draw(self,surface):
        surface.fill((12,10,24))
        pygame.draw.rect(surface, (24,20,44), (0,120,W,H-120)) #floor
        #enemy name + HP bar
        name = self.ft.render(self.enemy.name, False, DIALOGUE_NC)
        surface.blit(name, (W//2 - name.get_width()//2,12))
        draw_bar(surface, W//2 - 40,26,80,6,self.enemy_hp_shown,self.enemy.max_hp, (200,60,60))
        #enemy
        if self.phase != "win_msg":
            ox = int(math.sin(self.shake*60)*3) if self.shake > 0 else 0
            pygame.draw.ellipse(surface, (0,0,0), (W//2-24,86,48,12))
            surface.blit(self.sprite, (W//2-24 + ox, 40))
        #message box
        box = pygame.Rect(8,140,W-16,50)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill (DIALOGUE_BG)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, DIALOGUE_BORDER, box, 1)
        y = box.y + 8
        for line in wrap_txt(self.ft, self.message, box.width - 12)[:3]:
            surface.blit(self.ft.render(line,False, TXT_COLOR), (box.x+6,y))
            y += 12
        if self.phase != "menu":
            hint = self.ft.render("[E]", False, DIALOGUE_NC)
            surface.blit(hint, (box.right - hint.get_width() - 6, box.bottom -12))
        #hero panel
        panel = pygame.Rect(8,200,160,62)
        pygame.draw.rect(surface,(10,10,25),panel)
        pygame.draw.rect(surface, DIALOGUE_BORDER, panel, 1)
        surface.blit(self.ft.render("Hero", False, DIALOGUE_NC), (panel.x+8, panel.y +8))
        lv = "LV " + str(self.player.level) + "  XP " + str(self.player.xp) + "/" + str(self.player.xp_to_next())
        lv_img = self.ft.render(lv, False, TXT_COLOR)
        surface.blit(lv_img, (panel.right - lv_img.get_width() -8,panel.y+8))
        hp_txt = "HP " + str(self.hero.hp) + "/" + str(self.hero.max_hp)
        surface.blit(self.ft.render(hp_txt, False, TXT_COLOR), (panel.x + 8, panel.y + 22))
        draw_bar(surface, panel.x + 8, panel.y + 40, 144,8, self.hero_hp_shown, self.hero.max_hp, (80,200,120))

        #action btns
        for i, opt in enumerate(self.options):
            r = pygame.Rect(180+i*98,214,90,28)
            active = self.phase == "menu"
            selected = active and i == self.cursor
            if selected:
                border = DIALOGUE_NC
            elif active:
                border = DIALOGUE_BORDER
            else:
                border = (90,90,110)
            txt = opt
            if opt == "Item":
                count = count_kind(self.player.inventory, "heal")
                txt += " (" +str(count) +")"
            pygame.draw.rect(surface, (10,10,25), r)
            pygame.draw.rect(surface, border, r, 2 if selected else 1)
            label = self.ft.render(("> " if selected else "") +txt, False, border)
            surface.blit(label, label.get_rect(center=r.center))
        if self.phase == "menu":
            hint = self.ft.render("A/D move    E confirm", False, (140,140,160))
            surface.blit(hint, (180,248))
        #popups
        for p in self.popups:
            p.draw(surface, self.big)