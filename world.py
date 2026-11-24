import pygame
from settings import *

#temp '#' = wall, '.' = floor (each row 30 chars)
TOWN_MAP = [
    "##############################",
    "#............................#",
    "#............................#",
    "#.....##...............##....#",
    "#.....##...............##....#",
    "#............................#",
    "#............................#",
    "#............................#",
    "#............................#",
    "#............................#",
    "#............................#",
    "#.....##...............##....#",
    "#.....##...............##....#",
    "#............................#",
    "#............................#",
    "##############################",
]

class World:
    def __init__(self, tile_map):
        self.tile_map = tile_map
    def draw(self,surface):
        for row_i, row in enumerate(self.tile_map):
            for col_i, tile in enumerate(row):
                x = col_i * TILE_SIZE
                y = row_i * TILE_SIZE
                color = WALL_COLOR if tile == "#" else FLOOR_COLOR
                pygame.draw.rect(surface,color, (x,y,TILE_SIZE,TILE_SIZE))