import pygame
from settings import *

class NPC:
    def __init__(self, x,y,name,get_lines, color=NPC_COLOR, on_done=None, marker=None):
        self.pos = pygame.Vector2(x,y)
        self.name = name
        self.get_lines = get_lines
        self.on_done = on_done
        self.marker = marker #for "!" above NPC       
        self.size = NPC_SIZE
        #placeholder
        self.sprite = pygame.Surface((self.size, self.size))
        self.sprite.fill(color)

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)

    def draw(self,surface,camera):
        surface.blit(self.sprite, (int(self.pos.x) - int(camera.x), int(self.pos.y) - int(camera.y)))