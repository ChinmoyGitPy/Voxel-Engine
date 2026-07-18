import os
import random
import pygame as py
from OpenGL.GL import (
    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_NEAREST,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_REPEAT, GL_RGBA,
    GL_UNSIGNED_BYTE, glGenTextures, glBindTexture, glTexParameteri,
    glTexImage2D
)

from . import config
from .blocks import fallback_colours,grass,dirt,wood,leaves,water

texture_filenames = {
    grass: ["grass.jpg","grass.png"],
    dirt: ["dirt.jpg","dirt.png"],
    wood:["wood.jpg","wood.png"],
    leaves: ["leaves.jpg","leaves.png"],
    water: ["water.jpg","water.png"]
}

def _make_fallback_surface(colour,size=64):
    surf = py.Surface((size,size))
    surf.fill(colour)
    rng = random.Random(sum(colour))
    shade = py.Surface((size,size),py.SRCALPHA)
    for _ in range(140):
        x = rng.randrange(size)
        y = rng.randrange(size)
        d = rng.randrange(-14,14)
        c = tuple(max(0,min(255,ch+d))for ch in colour)
        shade.set_at((x,y),(*c,255))
    surf.blit(shade,(0,0,))
    return surf

def load_texture(block,filenames):
    surf = None
    for fname in filenames:
        path = os.path.join(config,ASSET_DIR,fname)
        if os.path.exists(path):
            try:
                surf = py.image.load(path)
                break
            except Exception:
                surf = None
    if surf is None:
        surf = _make_fallback_surface(fallback_colours[block])

    surf = surf.convert_alpha() if surf.get_flags() & py.SRCALPHA else surf.convert()
    tex_data = py.image.tostring(surf,"RGBA",True)
    w,h = surf.get_width(), surf.get_height()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
    return tex_id

def load_all_textures():
    return {
        block: load_texture(block,filenames)
        for block, filenames in texture_filenames.items()
    }