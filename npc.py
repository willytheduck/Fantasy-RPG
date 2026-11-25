import pygame
from settings import *

class NPC:
    def __init__(self, x,y,name,color=NPC_COLOR):
        self.pos = pygame.Vector2(x,y)
        self.name = name
        self.size = NPC_SIZE
        #placeholder
        self.sprite = pygame.Surface((self.size, self.size))
        self.sprite.fill(color)

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)

    def draw(self,surface,camera):
        surface.blit(self.sprite, (int(self.pos.x) - int(camera.x), int(self.pos.y) - int(camera.y)))