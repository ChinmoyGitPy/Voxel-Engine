import math
from OpenGL.GL import glDeleteBuffers
from . import config
from .blocks import air,solid_blocks
from .chunk import Chunk

class World:
    def __init__(self):
        self.chunks = {}

    def world_to_chunk(self, wx,wz):
        return wx//config.chunk_size,wz//config.chunk_size
    
    def get_chunk(self,cx,cz,create=True):
        key = (cx,cz)
        chunk = self.chunks.get(key)
        if chunk is None and create:
            chunk = Chunk(cx,cz)
            chunk.generate()
            self.chunks[key] = chunk
            
            for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)):
                nb = self.chunks.get((cx+dx,cz+dz))
                if nb is not None:
                    nb.mesh_dirty = True
        return chunk
    
    def get_block(self,wx,wy,wz):
        if wy < 0 or wy >= config.world_height:
            return air
        cx,cz = self.world_to_chunk(wx,wz)
        chunk = self.chunks.get((cx,cz))
        if chunk is None:
            return air
        lx = wx - cx * config.chunk_size
        lz = wz -cz * config.chunk_size
        return int(chunk.blocks[lx,wy,lz])

    def set_block(self,wx,wy,wz,block):
        if wy < 0 or wy >= config.world_height:
            return
        cx, cz = self.world_to_chunk(wx,wz)
        chunk = self.get_chunk(cx,cz,create=True)
        lx = wx - cx * config.chunk_size
        lz = wz - cz * config.chunk_size
        chunk.blocks[lx,wy,lz] = block
        chunk.mesh_dirty = True

        size = config.chunk_size
        if lx == 0:
            nb = self.chunks.get((cx -1,cz))
            if nb: nb.mesh_dirty = True
        if lx == size - 1:
            nb = self.chunks.get((cx+1,cz))
            if nb: nb.mesh_dirty = True
        if lz == 0:
            nb = self.chunks.get((cx,cz-1))
            if nb: nb.mesh_dirty = True
        if lz == size-1:
            nb = self.chunks.get((cx,cz+1))
            if nb: nb.mesh_dirty = True

    def is_solid(self,wx,wy,wz):
        return self.get_block(wx,wy,wz) in solid_blocks
    
    def ensure_chunks_around(self,wx,wz):
        pcx,pcz = self.world_to_chunk(int(math.floor(wx)),int(math.floor(wz)))
        rd = config.render_distance

        for dx in range(-rd,rd+1):
            for dz in range(-rd,rd+1):
                key = (pcx + dx, pcz + dz)
                if key not in self.chunks:
                    self.get_chunk(key[0],key[1],create=True)

        margin = rd + config.chunk_unload_margin
        to_unload = [
            key for key in self.chunks
            if abs(key[0] - pcx) > margin or abs(key[1] - pcz) > margin
        ]
        for key in to_unload:
            chunk = self.chunks.pop(key)
            for vbo in chunk.block_buffers.values():
                try:
                    glDeleteBuffers(1,[vbo])
                except Exception:
                    pass