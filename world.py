import pygame
from settings import *
def build_town(cols=50, rows=30):
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    for c in range(cols):
        grid[0][c]="#"
        grid[rows-1][c] = "#"
    for r in range(rows):
        grid[r][0] = "#"
        grid[r][cols-1] = "#"

    #2x2 pillars
    for pc,pr in [(8,6), (38,6),(8,20),(38,20), (23,13)]:
        for dr in range(2):
            for dc in range(2):
                grid[pr+dr][pc+dc] = "#"
    return ["".join(row) for row in grid]

TOWN_MAP = build_town()

class World:
    def __init__(self, tile_map):
        self.tile_map = tile_map
        self.cols = len(tile_map[0])
        self.rows = len(tile_map)
        self.width = self.cols*TILE_SIZE
        self.height = self.rows*TILE_SIZE
    def is_wall(self,col,row):
        if col <0 or row<0 or col>=self.cols or row >= self.rows:
            return True
        return self.tile_map[row][col] == "#"
    def collides(self,rect):
        left = rect.left//TILE_SIZE
        right = (rect.right - 1)//TILE_SIZE
        top = rect.top//TILE_SIZE
        bottom = (rect.bottom - 1)//TILE_SIZE
        for r in range(top, bottom +1):
            for c in range(left, right+1):
                if self.is_wall(c,r):
                    return True
        return False
    def draw_floor(self, surface, camera):
        cam_x, cam_y = int(camera.x), int(camera.y)
        start_col = max(0, cam_x//TILE_SIZE)
        end_col = min(self.cols, (cam_x+W)//TILE_SIZE+1)
        start_row = max(0,cam_y//TILE_SIZE)
        end_row = min(self.rows,(cam_y+H)//TILE_SIZE+1)
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                if self.tile_map[r][c] != "#":
                    x = c*TILE_SIZE - cam_x
                    y = r*TILE_SIZE - cam_y
                    pygame.draw.rect(surface, FLOOR_COLOR, (x,y,TILE_SIZE, TILE_SIZE))
    def draw_wall(self,surface, camera, c, r):
        x = c*TILE_SIZE - int(camera.x)
        y = r*TILE_SIZE - int(camera.y)
        top_y = y - WALL_HEIGHT #top face shifted up
        below_is_wall = r+1<self.rows and self.tile_map[r+1][c] == "#"
        if not below_is_wall:
            #front face
            pygame.draw.rect(surface, WALL_FRONT_COLOR, (x, top_y+TILE_SIZE, TILE_SIZE, WALL_HEIGHT))
        pygame.draw.rect(surface, WALL_TOP_COLOR, (x, top_y, TILE_SIZE, TILE_SIZE))
    def wall_items(self, surface, camera):
        #ret (sort_y, draw_func) every visible wal
        cam_x, cam_y = int(camera.x), int(camera.y)
        start_col = max(0, cam_x//TILE_SIZE)
        end_col = min(self.cols, (cam_x+W)//TILE_SIZE+1)
        start_row = max(0, cam_y//TILE_SIZE)
        #+WALL_HEIGHT cuz tall wals below the screen poke up into view
        end_row = min(self.rows, (cam_y+H+WALL_HEIGHT)//TILE_SIZE+1)
        items = []
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                if self.tile_map[r][c] == "#":
                    items.append(((r+1)*TILE_SIZE, lambda c=c, r=r: self.draw_wall(surface, camera, c, r)))
        return items