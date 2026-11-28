import math
import pygame
from settings import *
from player import Player
from world import World, TOWN_MAP, DUNGEON_MAP
from npc import NPC
from enemy import OverworldEnemy
from chest import Chest
from door import Door
from stats import make_enemy_stats
from battle import Battle
from utils import draw_shadow
from ui import DialogueBox, ShopMenu, InventoryMenu
import story
from story import flags

pygame.init()
screen = pygame.display.set_mode((W * SCALE, H * SCALE))
pygame.display.set_caption("Fantasy RPG")
canvas = pygame.Surface((W, H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 16)

player = Player(3 * TILE_SIZE, 5 * TILE_SIZE)
dialogue = DialogueBox(ft)
shop = ShopMenu(ft, story.SHOP_STOCK)
inv_menu = InventoryMenu(ft)
camera = pygame.Vector2(0, 0)
state = "town"
talking_to = None

# battle info
battle = None
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

#areas
areas = {
    "town": {
        "world": World(TOWN_MAP),
        "npcs": [
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
        ],
        "enemies": [],
        "chests": [],
        "doors": [
            Door(47,14,2,2,"dungeon", (5,16), "Hollow Cave", lock_flag="quest_accepted", lock_lines=["* A dark cave mouth yawns in front of you.", "* Maybe you should talk to the Elder first."], bounce=(-24,0)),
        ],
        "spawn": (3,5),
    },
    "dungeon": {
        "world": World(DUNGEON_MAP, DUNGEON_FLOOR, DUNGEON_WALL_TOP, DUNGEON_WALL_FRONT),
        "npcs": [],
        "enemies": [
            OverworldEnemy(20*TILE_SIZE, 6*TILE_SIZE,"Glowmoth"),
            OverworldEnemy(23*TILE_SIZE, 10*TILE_SIZE, "Mossling"),
            OverworldEnemy(19*TILE_SIZE, 27*TILE_SIZE, "Glowmoth"),
            OverworldEnemy(23*TILE_SIZE, 24*TILE_SIZE, "Mossling"),
            OverworldEnemy(36*TILE_SIZE, 14*TILE_SIZE, "Glowmoth"),
            OverworldEnemy(35*TILE_SIZE, 18*TILE_SIZE, "Mossling"),
            OverworldEnemy(40*TILE_SIZE,19*TILE_SIZE,"Dusty Knight"),
            OverworldEnemy(39*TILE_SIZE, 4*TILE_SIZE, "Dusty Knight"),
            OverworldEnemy(41*TILE_SIZE, 28*TILE_SIZE, "Warden of Ash"),
        ],
        "chests": [
            Chest(8*TILE_SIZE, 14*TILE_SIZE, item="Star-berry Tea"),
            Chest(17*TILE_SIZE, 10*TILE_SIZE, coins=15),
            Chest(25*TILE_SIZE, 23*TILE_SIZE, coins=10, item="Star-berry Tea"),
            Chest(43*TILE_SIZE, 3*TILE_SIZE, coins=30, item="Patchwork Cloak"),
        ],
        "doors": [
            Door(2,16,2,2,"town",(45,14), "Cinderwick"),
        ],
        "spawn": (5,16),
    },
}

current_area = "town"
world = areas["town"]["world"]
npcs = areas["town"]["npcs"]
enemies = areas["town"]["enemies"]
chests = areas["town"]["chests"]
doors = areas["town"]["doors"]

def enter_area(name, spawn=None):
    global current_area, world, npcs, enemies, chests, doors
    area = areas[name]
    current_area = name
    world = area["world"]
    npcs = area["npcs"]
    enemies = area["enemies"]
    chests = area["chests"]
    doors = area["doors"]
    sx, sy = spawn if spawn else area["spawn"]
    player.pos = pygame.Vector2(sx*TILE_SIZE, sy*TILE_SIZE)


def find_nearby():
    zone = player.rect().inflate(16,16)
    for thing in npcs + chests:
        if isinstance(thing, Chest) and thing.opened:
            continue
        if zone.colliderect(thing.rect()):
            return thing
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
                    thing = find_nearby()
                    if thing:
                        talking_to = thing
                        if isinstance(thing, Chest):
                            dialogue.start("Chest", thing.open(player))
                        else:
                            dialogue.start(thing.name, thing.get_lines())
                        state = "dialogue"
                elif event.key == pygame.K_i:
                    inv_menu.reset()
                    state = "inventory"
                    # temp keys
                elif event.key == pygame.K_3:
                    state = "menu"
                elif event.key == pygame.K_4:
                    flags["has_ember"] = True  # for testing
                elif event.key == pygame.K_5:
                    player.stats.heal(999)
            elif state == "dialogue":
                if event.key == pygame.K_e:
                    dialogue.advance()
                    if not dialogue.active:
                        nxt = talking_to.on_done() if talking_to and talking_to.on_done else None
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
            elif state == "inventory":
                if event.key in (pygame.K_w, pygame.K_UP):
                    inv_menu.move(-1, player)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    inv_menu.move(1, player)
                elif event.key in (pygame.K_e, pygame.K_RETURN):
                    inv_menu.use(player)
                elif event.key in (pygame.K_q, pygame.K_i, pygame.K_ESCAPE):
                    state = "town"
            elif state == "combat":
                battle.handle_key(event.key)
            elif state == "menu":
                if event.key == pygame.K_1:
                    state = "town"
    if state == "combat" and battle.result:
        res = battle.result
        story_lines = None
        if res == "win":
            enemies.remove(battle_enemy)
            if battle_stats.boss:
                flags["has_ember"] = True
                story_lines = [
                    "* The Warden of Ash crumbles into warm, quiet ash.",
                    "* It was only keeping the ember warm. You can almost hear it say sorry.",
                    "* In the middle of the ash, a tiny ember glows. It hums like a kettle.",
                    "* You carefully pick it up. (Quest updated.)",
                ]
        elif res == "flee":
            battle_enemy.cooldown = 2.5
        elif res == "lose":
            player.stats.hp = player.stats.max_hp
            battle_enemy.cooldown = 2.5
            enter_area("town")
        battle = None
        battle_enemy = None
        state = "town"
        if story_lines:
            talking_to = None
            dialogue.start("Ember", story_lines)
            state = "dialogue"

    keys = pygame.key.get_pressed()
    canvas.fill(BG_COLOR)
    # upd
    if state == "town":
        player.update(keys, dt, world, npcs + chests)
        #doors
        for d in doors:
            if player.rect().colliderect(d.rect()):
                if d.locked():
                    player.pos += pygame.Vector2(d.bounce)
                    talking_to = d
                    dialogue.start(d.label, d.lock_lines)
                    state = "dialogue"
                else:
                    enter_area(d.target, d.spawn)
                break
    if state == "town":
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
            battle = Battle(ft, player, battle_stats, battle_enemy.sprite)
            state = "combat"
    elif state == "combat":
        battle.update(dt)
    # draw
    if state in ("town", "dialogue", "shop", "encounter", "inventory"):
        # camera follow player
        camera.x = player.pos.x + player.size / 2 - W / 2
        camera.y = player.pos.y + player.size / 2 - H / 2
        camera.x = max(0, min(camera.x, world.width - W))
        camera.y = max(0, min(camera.y, world.height - H))
        world.draw_floor(canvas, camera)
        for d in doors:
            d.draw(canvas, camera)
        # shadows
        draw_shadow(canvas, camera, player.rect())
        for npc in npcs:
            draw_shadow(canvas, camera, npc.rect())
        for e in enemies:
            draw_shadow(canvas, camera, e.rect())
        for ch in chests:
            draw_shadow(canvas, camera, ch.rect())
        # depth sort
        items = world.wall_items(canvas, camera)
        items.append((player.rect().bottom, lambda: player.draw(canvas, camera)))
        for npc in npcs:
            items.append((npc.rect().bottom, lambda n=npc: n.draw(canvas, camera)))
        for e in enemies:
            items.append((e.rect().bottom, lambda en=e: en.draw(canvas, camera)))
        for ch in chests:
            items.append((ch.rect().bottom, lambda c=ch: c.draw(canvas, camera)))
        items.sort(key=lambda item: item[0])
        for _, draw in items:
            draw()
        if state == "town":
            near = find_nearby()
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
                label = "[E] Open" if isinstance(near, Chest) else "[E] Talk"
                prompt = ft.render(label, False, TXT_COLOR)
                px = near.pos.x - camera.x + near.size / 2 - prompt.get_width() / 2
                py = near.pos.y - camera.y - 12
                canvas.blit(prompt, (int(px), int(py)))
            # HUD
            hud = (
                "LV " + str(player.level) +
                "  HP "
                + str(player.stats.hp)
                + "/"
                + str(player.stats.max_hp)
                + "  XP " + str(player.xp) + "/" + str(player.xp_to_next())
                + "   Coins: "
                + str(player.coins)
            )
            canvas.blit(
                ft.render(hud, False, TXT_COLOR), (6, 5)
            )
            canvas.blit(ft.render(story.quest_txt(), False, DIALOGUE_NC), (6, 16))
            canvas.blit(ft.render("[I] Bag", False, (140,140,160)), (6,27))
        dialogue.draw(canvas)
        if state == "shop":
            shop.draw(canvas, player)
        if state == "inventory":
            inv_menu.draw(canvas, player)
        if state == "encounter" and int(encounter_timer * 10) % 2 == 0:
            canvas.blit(flash, (0, 0))

    elif state == "combat":
        battle.draw(canvas)

    elif state == "menu":
        txt = ft.render("MENU (placeholder) - press 1", True, (255, 255, 255))
        canvas.blit(txt, (150, 130))

    scald = pygame.transform.scale(canvas, screen.get_size())
    screen.blit(scald, (0, 0))
    pygame.display.flip()

pygame.quit()
