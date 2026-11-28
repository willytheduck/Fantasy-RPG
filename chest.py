import pygame
from settings import *

class Chest:
    def __init__(self,x,y,coins=0, item = None):
        self.pos = pygame.Vector2(x,y)
        self.size = CHEST_SIZE
        self.coins = coins
        self.item = item
        self.opened = False
        self.name = "Chest"
        self.on_done = None

        self.closed_sprite = pygame.Surface((self.size, self.size))
        self.closed_sprite.fill((140,90,40))
        pygame.draw.rect(self.closed_sprite,(200,160,60), (0,5,self.size,3))
        pygame.draw.rect(self.closed_sprite, (240,220,120),(6,4,4,5))
        self.open_sprite = pygame.Surface((self.size, self.size))
        self.open_sprite.fill((70,45,25))
        pygame.draw.rect(self.open_sprite, (30,20,10), (2,2, self.size - 4,6))

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)
    def open(self, player):
        self.opened = True
        lines = []
        if self.coins > 0:
            player.coins += self.coins
            lines.append("* You found " + str(self.coins) + " coins!")
        if self.item:
            player.inventory[self.item] = player.inventory.get(self.item,0)+1
            lines.append("* You found a " + self.item +"!")
        if not lines:
            lines.append("* The chest is empty...")
        return lines
    def draw(self, surface, camera):
        sprite = self.open_sprite if self.opened else self.closed_sprite
        surface.blit(sprite, (int(self.pos.x) - int(camera.x), int(self.pos.y) - int(camera.y)))