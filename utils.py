import pygame
from settings import *
_shadow_cache = {}
def draw_shadow(surface, camera, rect):
    w = rect.width
    h = max(4, rect.width//3)
    key = (w,h)
    #to save my CPU
    if key not in _shadow_cache:
        s = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, SHADOW_COLOR, (0,0,w,h))
        _shadow_cache[key] = s
    x = rect.x - int(camera.x)
    y = rect.bottom - h//2 - int(camera.y)
    surface.blit(_shadow_cache[key], (x,y))
