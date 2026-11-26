import math
import pygame
from settings import *

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

class Battle:
    def __init__(self,ft,player,enemy,enemy_sprite):
        self.ft = ft
        self.hero = player.stats
        self.enemy = enemy
        self.sprite = pygame.transform.scale(enemy_sprite, (48,48))
        self.options = ["Attack", "Item", "Run"]
        self.cursor = 0
        self.phase = "intro"
        self.message = "* " + enemy.name + " blocks the way!"
        self.shake = 0.0
        self.result = None #"win", "lose" or "flee" when the battle is over

    def damage(self, attacker, defender):
        #placeholder
        return max(1, attacker.attack - defender.defense)

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
            dmg = self.damage(self.hero, self.enemy)
            self.enemy.take_dmg(dmg)
            self.shake = 0.3
            self.message = "* You strike " + self.enemy.name + " for " + str(dmg) + " damage!"
            self.phase = "player_msg"
        elif option == "Item":
            self.message = "* You have no usable items yet."
            self.phase = "notice" #no turn used
        elif option == "Run":
            self.message = "* You fleed."
            self.phase = "flee_msg"
    def advance(self):
        name = self.enemy.name
        if self.phase in ("intro", "notice"):
            self.to_menu()
        elif self.phase == "player_msg":
            if not self.enemy.is_alive():
                self.message = ("* " + name + " was defeated! You gain " + str(self.enemy.xp_reward)+ " XP and " + str(self.enemy.coin_reward) + " coins.")
                self.phase = "win_msg"
            else:
                dmg = self.damage(self.enemy, self.hero)
                self.hero.take_dmg(dmg)
                self.message = "* " + name + " attacks! You take " + str(dmg) + " damage."
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
    def draw(self,surface):
        surface.fill((12,10,24))
        pygame.draw.rect(surface, (24,20,44), (0,120,W,H-120)) #floor
        #enemy name + HP bar
        name = self.ft.render(self.enemy.name, False, DIALOGUE_NC)
        surface.blit(name, (W//2 - name.get_width()//2,12))
        draw_bar(surface, W//2 - 40,26,80,6,self.enemy.hp,self.enemy.max_hp, (200,60,60))
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
        hp_txt = "HP " + str(self.hero.hp) + "/" + str(self.hero.max_hp)
        surface.blit(self.ft.render(hp_txt, False, TXT_COLOR), (panel.x + 8, panel.y + 22))
        draw_bar(surface, panel.x + 8, panel.y + 40, 144,8, self.hero.hp, self.hero.max_hp, (80,200,120))

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
            pygame.draw.rect(surface, (10,10,25), r)
            pygame.draw.rect(surface, border, r, 2 if selected else 1)
            label = self.ft.render(("> " if selected else "") +opt, False, border)
            surface.blit(label, label.get_rect(center=r.center))
        if self.phase == "menu":
            hint = self.ft.render("A/D move    E confirm", False, (140,140,160))
            surface.blit(hint, (180,248))