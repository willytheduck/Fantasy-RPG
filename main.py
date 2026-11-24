import pygame
from settings import *
from player import Player
from world import World, TOWN_MAP

pygame.init()
screen = pygame.display.set_mode((W*SCALE, H*SCALE))
pygame.display.set_caption("Fantasy RPG")
canvas = pygame.Surface((W,H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 16)

player = Player(3*TILE_SIZE, 5*TILE_SIZE)
town = World(TOWN_MAP)
state = "town"

running = True
while running:
    dt = clock.tick(FPS)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #temp keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                state = "town"
            elif event.key == pygame.K_2:
                state = "combat"
            elif event.key == pygame.K_3:
                state = "menu"

    keys = pygame.key.get_pressed()
    canvas.fill(BG_COLOR)

    if state == "town":
        player.update(keys, dt)
        town.draw(canvas)
        player.draw(canvas)
    elif state == "combat":
        txt = ft.render("COMBAT (placeholder)", True, (255,255,255))
        canvas.blit(txt,(170,130))
    elif state == "menu":
        txt = ft.render("MENU (placeholder)", True, (255,255,255))
        canvas.blit(txt, (170,130))

    scald = pygame.transform.scale(canvas, screen.get_size())
    screen.blit(scald, (0,0))
    pygame.display.flip()

pygame.quit()