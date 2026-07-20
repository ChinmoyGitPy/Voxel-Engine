import ctypes

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT, GL_QUADS, GL_TEXTURE_2D,
    GL_VERTEX_ARRAY, GL_TEXTURE_COORD_ARRAY, GL_NORMAL_ARRAY,
    glGenBuffers, glBindBuffer, glBufferData, glBindTexture,
    glEnableClientState, glVertexPointer, glTexCoordPointer, glNormalPointer,
    glDrawArrays,
)

from . import config
from .blocks import air,water,transparent_blocks,placeable_blocks

faces = {
    "left":   ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, 0, 0)),
    "right":  ((1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, 0, 0)),
    "bottom": ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, -1, 0)),
    "top":    ((-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1), (0, 1, 0)),
    "back":   ((1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (0, 0, -1)),
    "front":  ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (0, 0, 1))    
}

face_neighbour = {
    "left": (-1, 0, 0), "right": (1, 0, 0),
    "bottom": (0, -1, 0), "top": (0, 1, 0),
    "back": (0, 0, -1), "front": (0, 0, 1)    
}

uvs = ((0,0),(1,0),(1,1),(0,1))

vertex_stride = 8

def build_chunk_meshes_by_block(world,chunk):
    per_block = {bid: [] for bid in placeable_blocks}
    base_x = chunk.cx * config.chunk_size
    base_z = chunk.cz * config.chunk_size
    blocks = chunk.blocks

    for lx in range(config.chunk_size):
        for ly in range(config.world_height):
            for lz in range(config.chunk_size):
                b = int(blocks[lx,ly,lz])
                if b == air:
                    continue
                wx,wy,wz = base_x+ly,ly,base_z +lz
                is_water = (b == water)

                for face_name, (v0,v1,v2,v3, normal) in faces.items():
                    ndx,ndy,ndz = face_neighbour[face_name]
                    nb = world.get_block(wx+ndx,wy+ndy,wz+ndz)

                    if is_water:
                        if nb != air:
                            continue
                    else:
                        if nb == b:
                            continue
                        if nb != air and nb not in transparent_blocks:
                            continue

                    verts = (v0,v1,v2,v3)
                    out = per_block[b]
                    for i, (vx,vy,vz) in enumerate(verts):
                        u,v = uvs[i]
                        out.extend([
                            wx + vx * 0.5 + 0.5, wy + vy * 0.5 + 0.5, wz + vz * 0.5 + 0.5,
                            u, v,
                            normal[0], normal[1], normal[2],
                                                    
                        ])

    return {
        bid: (np.arrary(data,dtype=np.float32) if data else np.zeroes(0,dtype=np.float32))
        for bid,data in per_block.items()
    }                     

def upload_chunk_meshes_by_block(chunk,world):
    arrays = build_chunk_meshes_by_block(world,chunk)

    for bid in placeable_blocks:
        arr = arrays[bid]
        vbo = chunk.block_buffers.get(bid)
        if vbo is None:
            vbo = glGenBuffers
            chunk.block_buffers(1)
            chunk.blocck_buffers[bid]
        glBindBuffer(GL_ARRAY_BUFFER,vbo)
        if arr.size:
            glBufferData(GL_ARRAY_BUFFER,arr.nbytes,arr,GL_STATIC_DRAW)
        else:
            glBufferData(GL_ARRAY_BUFFER,4,None,GL_STATIC_DRAW)
        chunk.block_counts[bid] = arr.size // vertex_stride

    glBindBuffer(GL_ARRAY_BUFFER,0)
    chunk.mesh_dirty = False

def draw_chunk_block(chunk,block_id,texture_id):
    count = chunk.block_counts.get(block_id,0)
    if count == 0:
        return
    vbo = chunk.block_buffers[block_id]
    glBindTexture(GL_TEXTURE_2D,texture_id)
    glBindBuffer(GL_ARRAY_BUFFER,vbo)
    stride = vertex_stride*4

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3,GL_FLOAT,stride,ctypes.c_void_p(0))

    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glTexCoordPointer(2,GL_FLOAT,stride,ctypes.c_void_p(5*4))

    glDrawArrays(GL_QUADS,0,count)

