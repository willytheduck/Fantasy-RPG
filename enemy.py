import pygame
from settings import *
from stats import ENEMY_TYPE

class OverworldEnemy:
    def __init__(self,x,y,kind):
        self.pos = pygame.Vector2(x,y)
        self.kind = kind
        self.size = ENEMY_TYPE[kind].get("size", ENEMY_SIZE)
        self.cooldown = 0.0 #cd for enemy
        #placeholder
        self.sprite = pygame.Surface((self.size, self.size))
        self.sprite.fill(ENEMY_TYPE[kind]["color"])
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)
    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
    def can_trigger(self):
        return self.cooldown <=0
    def draw(self,surface,camera):
        #blink while on cd
        if self.cooldown > 0 and int(self.cooldown*10) % 2 ==0:
            return
        surface.blit(self.sprite, (int(self.pos.x) - int(camera.x), int(self.pos.y) - int(camera.y)))