import pygame
import math
from settings import *
from player import Player
from world import World, TOWN_MAP
from npc import NPC
from enemy import OverworldEnemy
from stats import make_enemy_stats
from utils import draw_shadow
from ui import DialogueBox, ShopMenu
import story
from story import flags

pygame.init()
screen = pygame.display.set_mode((W * SCALE, H * SCALE))
pygame.display.set_caption("Fantasy RPG")
canvas = pygame.Surface((W, H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 16)

player = Player(3 * TILE_SIZE, 5 * TILE_SIZE)
town = World(TOWN_MAP)
dialogue = DialogueBox(ft)
shop = ShopMenu(ft, story.SHOP_STOCK)
camera = pygame.Vector2(0, 0)
state = "town"
talking_to = None

# battle info
battle_enemy = None
battle_stats = None
encounter_timer = 0.0
flash = pygame.Surface((W, H), pygame.SRCALPHA)
flash.fill((255, 255, 255, 150))


def elder_done():
    if not flags["quest_accepted"]:
        flags["quest_accepted"] = True
        player.coins += 25
    return None


def shop_done():
    shop.reset()
    return "shop"


npcs = [
    NPC(
        14 * TILE_SIZE,
        8 * TILE_SIZE,
        "Elder",
        story.elder_lines,
        on_done=elder_done,
        marker=lambda: not flags["quest_accepted"],
    ),
    NPC(
        30 * TILE_SIZE,
        16 * TILE_SIZE,
        "Shopkeeper",
        story.shop_lines,
        (220, 170, 60),
        on_done=shop_done,
    ),
]

# temp
enemies = [
    OverworldEnemy(22 * TILE_SIZE, 5 * TILE_SIZE, "Mossling"),
    OverworldEnemy(40 * TILE_SIZE, 10 * TILE_SIZE, "Glowmoth"),
    OverworldEnemy(18 * TILE_SIZE, 24 * TILE_SIZE, "Dusty Knight"),
]


def find_nnpc():
    zone = player.rect().inflate(16, 16)
    for npc in npcs:
        if zone.colliderect(npc.rect()):
            return npc
    return None


running = True
while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == "town":
                if event.key == pygame.K_e:
                    npc = find_nnpc()
                    if npc:
                        talking_to = npc
                        dialogue.start(npc.name, npc.get_lines())
                        state = "dialogue"
                    # temp keys
                elif event.key == pygame.K_3:
                    state = "menu"
                elif event.key == pygame.K_4:
                    flags["has_ember"] = True  # for testing
            elif state == "dialogue":
                if event.key == pygame.K_e:
                    dialogue.advance()
                    if not dialogue.active:
                        nxt = talking_to.on_done() if talking_to.on_done else None
                        state = nxt or "town"
            elif state == "shop":
                if event.key in (pygame.K_w, pygame.K_UP):
                    shop.move(-1)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    shop.move(1)
                elif event.key in (pygame.K_e, pygame.K_RETURN):
                    shop.buy(player)
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    state = "town"
            elif state == "combat":
                # temp
                if event.key == pygame.K_e:
                    player.coins += battle_stats.coin_reward
                    player.xp += battle_stats.xp_reward
                    enemies.remove(battle_enemy)
                    battle_enemy = None
                    state = "town"
                elif event.key == pygame.K_q:
                    battle_enemy.cooldown = 2.5
                    battle_enemy = None
                    state = "town"
            elif state == "menu":
                if event.key == pygame.K_1:
                    state = "town"

    keys = pygame.key.get_pressed()
    canvas.fill(BG_COLOR)
    # upd
    if state == "town":
        player.update(keys, dt, town, npcs)
        for e in enemies:
            e.update(dt)
        for e in enemies:
            if e.can_trigger() and player.rect().colliderect(e.rect()):
                battle_enemy = e
                battle_stats = make_enemy_stats(e.kind)
                encounter_timer = 0.7
                state = "encounter"
                break
    elif state == "dialogue":
        dialogue.update(dt)
    elif state == "encounter":
        encounter_timer -= dt
        if encounter_timer <= 0:
            state = "combat"
    # draw
    if state in ("town", "dialogue", "shop", "encounter"):
        # camera follow player
        camera.x = player.pos.x + player.size / 2 - W / 2
        camera.y = player.pos.y + player.size / 2 - H / 2
        camera.x = max(0, min(camera.x, town.width - W))
        camera.y = max(0, min(camera.y, town.height - H))
        town.draw_floor(canvas, camera)
        # shadows
        draw_shadow(canvas, camera, player.rect())
        for npc in npcs:
            draw_shadow(canvas, camera, npc.rect())
        for e in enemies:
            draw_shadow(canvas, camera, e.rect())
        # depth sort
        items = town.wall_items(canvas, camera)
        items.append((player.rect().bottom, lambda: player.draw(canvas, camera)))
        for npc in npcs:
            items.append((npc.rect().bottom, lambda n=npc: n.draw(canvas, camera)))
        for e in enemies:
            items.append((e.rect().bottom, lambda en=e: en.draw(canvas, camera)))
        items.sort(key=lambda item: item[0])
        for _, draw in items:
            draw()
        if state == "town":
            near = find_nnpc()
            # bobbing "!"
            for n in npcs:
                if n is not near and n.marker and n.marker():
                    bob = int(math.sin(pygame.time.get_ticks() / 200) * 2)
                    mk = ft.render("!", False, DIALOGUE_NC)
                    mx = int(n.pos.x - camera.x + n.size / 2 - mk.get_width() / 2)
                    my = int(n.pos.y - camera.y - 12 + bob)
                    canvas.blit(mk, (mx, my))
            # [E] talk
            if near:
                prompt = ft.render("[E] Talk", False, TXT_COLOR)
                px = near.pos.x - camera.x + near.size / 2 - prompt.get_width() / 2
                py = near.pos.y - camera.y - 12
                canvas.blit(prompt, (int(px), int(py)))
            # HUD
            hud = (
                "HP "
                + str(player.stats.hp)
                + "/"
                + str(player.stats.max_hp)
                + "   Coins: "
                + str(player.coins)
            )
            canvas.blit(
                ft.render("Coins: " + str(player.coins), False, TXT_COLOR), (6, 5)
            )
            canvas.blit(ft.render(story.quest_txt(), False, DIALOGUE_NC), (6, 16))

        dialogue.draw(canvas)
        if state == "shop":
            shop.draw(canvas, player)
        if state == "encounter" and int(encounter_timer * 10) % 2 == 0:
            canvas.blit(flash, (0, 0))

    elif state == "combat":
        # temp
        canvas.fill((0, 0, 0))
        big = pygame.transform.scale(battle_enemy.sprite, (48, 48))
        canvas.blit(big, (W // 2 - 24, 50))
        lines = [
            "* " + battle_stats.name + " blocks the way!",
            battle_stats.name
            + " HP "
            + str(battle_stats.hp)
            + "/"
            + str(battle_stats.max_hp)
            + " ATK "
            + str(battle_stats.attack)
            + " DEF "
            + str(battle_stats.defense),
            "Hero HP " + str(player.stats.hp),
            "[E] win (temp)    [Q] run (temp)",
        ]
        y = 130
        for line in lines:
            canvas.blit(ft.render(line, False, TXT_COLOR), (W // 2 - 110, y))
            y += 16
    elif state == "menu":
        txt = ft.render("MENU (placeholder) - press 1", True, (255, 255, 255))
        canvas.blit(txt, (150, 130))

    scald = pygame.transform.scale(canvas, screen.get_size())
    screen.blit(scald, (0, 0))
    pygame.display.flip()

pygame.quit()
