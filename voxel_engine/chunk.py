import random
import numpy as np

from . import config
from .blocks import air,dirt,grass,water,wood,leaves
from .noise import height_at

_tree_rng = random.Random(config.tree_seed)

class Chunk:
    __slots__ = ("cx","cz","blocks","mesh_dirty","block_buffers","block_counts")

    def __init__(self,cx,cz):
        self.cx = cx
        self.cz = cz
        self.blocks = np.zeros(
            (config.chunk_size,config.world_height,config.chunk_size),dtype=np.uint8
        )
        self.mesh_dirty = True
        self.block_buffers  = {}
        self.block_counts = {}

    def generate(self):
        
        base_x = self.cx * config.chunk_size
        base_z = self.cz * config.chunk_size
        size = config.chunk_size
        sea_level = config.sea_level
        world_height = config.world_height

        for lx in range(size):
            for lz in range(size):
                wx = base_x + lx
                wz = base_z + lz
                h = height_at(wx,wz)

                for y in range(0,h-1):
                    self.blocks[lx,y,lz] = dirt
                self.blocks[lx,h-1,lz] = grass if h>sea_level else dirt

                for y in range(h,sea_level + 1):
                    if 0 <= y < world_height:
                        self.blocks[lx,y,lz] = water
                    
                if (h > sea_level and 2 <= lx <= size - 3 and 2 <= lz <= size - 3):
                    _tree_rng.seed((wx*676767 + wz*696969) & 0xFFFFFFFF)
                    if _tree_rng.random() < config.tree_chance:
                        self._place_tree(lx,h,lz)

    def _place_tree(self,lx,y0,lz):
        trunk_h = _tree_rng.randint(4,6)
        world_height_ = config.world_height
        size = config.chunk_size
        
        for i in range(trunk_h):
            y = y0 + i
            if y < world_height_:
                self.blocks[lx,y,lz] = wood

        top = y0 + trunk_h
        for dy in range (-2,2):
            ry = top + dy
            if ry < 0 or ry >= world_height_:
                continue
            radius = 2 if dy < 1 else 1
            for dx in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if dx == 0 and dz == 0 and dy < 1:
                        continue
                    if abs(dx) == radius and abs(dz) == radius and radius == 2:
                        continue
                    lxx, lzz = lx + dx, lz + dz
                    if 0 <= lxx < size and 0 <= lzz < size:
                        if self.blocks[lxx,ry,lzz] == air:
                            self.blocks[lxx,ry,lzz] = leaves 