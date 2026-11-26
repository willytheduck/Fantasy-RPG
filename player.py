import pygame
from settings import *
from stats import Stats

class Player:
    def __init__(self ,x,y):
        self.pos = pygame.Vector2(x, y)
        self.size = PLAYER_SIZE
        self.coins = 0
        self.inventory = {}
        self.stats = Stats("Hero", 30,6,2)
        self.xp = 0

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)

    def blocked(self,world,npcs):
        r = self.rect()
        if world.collides(r):
            return True
        for npc in npcs:
            if r.colliderect(npc.rect()):
                return True
        return False

    def update(self, keys, dt,world, npcs=()):
        move = pygame.Vector2(0,0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y +=1
        if keys[pygame.K_a]:
            move.x -=1
        if keys[pygame.K_d]:
            move.x +=1
        if move.length()>0:
            move = move.normalize()
        velocity = move *PLAYER_SPEED*dt

        #mov x, undo if hit wall
        self.pos.x += velocity.x
        if self.blocked(world, npcs):
            self.pos.x -= velocity.x
        #mov y, undo if hit wall
        self.pos.y += velocity.y
        if self.blocked(world, npcs):
            self.pos.y -= velocity.y

    def draw(self, surface, camera):
        r = self.rect()
        r.x -= int(camera.x)
        r.y -= int(camera.y)
        pygame.draw.rect(surface, PLAYER_COLOR, r)
        