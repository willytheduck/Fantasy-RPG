import pygame
from settings import *

class Player:
    def __init__(self,x,y):
        self.pos = pygame.Vector2(x,y)
        self.size = PLAYER_SIZE

    def update(self,keys,dt):
        move = pygame.Vector2(0,0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1

        #stop diagonal move 2 fast
        if move.length()>0:
            move = move.normalize()

        self.pos += move * PLAYER_SPEED * dt 

    def draw(self, surface):
        rect = pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)
        