import pygame
from settings import *
from story import flags
class Door:
    def __init__(self, col, row, w, h , target, spawn, label,lock_flag=None, lock_lines=None, bounce=(0,0)):
        self.area_rect = pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, w*TILE_SIZE, h*TILE_SIZE)
        self.target = target
        self.spawn = spawn
        self.label = label
        self.lock_flag = lock_flag
        self.lock_lines = lock_lines or ["* It's locked."]
        self.bounce = bounce
        self.on_done = None
    def rect(self):
        return self.area_rect
    def locked(self):
        return self.lock_flag is not None and not flags[self.lock_flag]
    def draw(self, surface, camera):
        r = self.area_rect.move(-int(camera.x), -int(camera.y))
        pygame.draw.rect(surface, (10,8,16),r)
        pygame.draw.rect(surface, (150,140,170), r, 2)