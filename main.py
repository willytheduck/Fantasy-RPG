import pygame
from settings import *
from player import Player
from world import World, TOWN_MAP
from npc import NPC
from utils import draw_shadow

pygame.init()
screen = pygame.display.set_mode((W*SCALE, H*SCALE))
pygame.display.set_caption("Fantasy RPG")
canvas = pygame.Surface((W,H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 16)

player = Player(3*TILE_SIZE, 5*TILE_SIZE)
town = World(TOWN_MAP)
npcs = [
    NPC(14*TILE_SIZE, 8*TILE_SIZE, "Elder"),
    NPC(30*TILE_SIZE, 16*TILE_SIZE, "Shopkeeper", (220,170,60)),
]
camera = pygame.Vector2(0,0)
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
        player.update(keys, dt, town, npcs)
        #camera follow player
        camera.x = player.pos.x + player.size/2 - W/2
        camera.y = player.pos.y + player.size/2-H/2
        camera.x = max(0,min(camera.x,town.width-W))
        camera.y = max(0,min(camera.y,town.height -H))
        town.draw_floor(canvas, camera)
        #shadows
        draw_shadow(canvas, camera, player.rect())
        for npc in npcs:
            draw_shadow(canvas,camera,npc.rect())
        #depth sort
        items = town.wall_items(canvas, camera)
        items.append((player.rect().bottom, lambda: player.draw(canvas, camera)))
        for npc in npcs:
            items.append((npc.rect().bottom, lambda n=npc: n.draw(canvas,camera)))
        items.sort(key=lambda item: item[0])
        for _, draw in items:
            draw()
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