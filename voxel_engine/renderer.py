from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
from . import config

def setup_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glShadeModel(GL_FLAT)

    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, config.sky_colour)
    glFogf(GL_FOG_START, config.fog_start_chunks * config.chunk_size)
    glFogf(GL_FOG_END, config.fog_end_chunks * config.chunk_size)

    glClearColor(*config.sky_colour)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.4, 1.0, 0.3, 0.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.55, 0.55, 0.6, 1.0))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.55, 0.55, 0.6, 1.0))
    glColor4f(1, 1, 1, 1)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 1, 1))

def set_perspective():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(config.fov, config.screen_w/config.screen_h,config.near_plane,config.far_plane,)
    glMatrixMode(GL_MODELVIEW)

def apply_camera(player):
    glLoadIdentity()
    ex,ey,ez= player.eye_pos()
    fx,fy,fz = player.forward_vector()
    gluLookAt(ex, ey, ez, ex + fx, ey + fy, ez + fz, 0, 1, 0)

def _begin_2d_overlay():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0,config.screen_w,config.screen_h,0,-1,1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

def _end_2d_overlay():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glColor3f(1,1,1)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_crosshair():
    _begin_2d_overlay()
    glDisable(GL_TEXTURE_2D)
    glColor3f(1,1,1)
    cx, cy = config.screen_w//2,config.screen_h//2
    s = 8
    glBegin(GL_LINES)
    glVertex2f(cx-s,cy)
    glVertex2f(cx +s,cy)
    glVertex2f(cx, cy - s)
    glVertex2f(cx, cy + s)
    glEnd()
    glEnable(GL_TEXTURE_2D)
    _end_2d_overlay()

def draw_hotbar(player,textures):
    _begin_2d_overlay()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

    slot_size = 56
    padding = 6
    inventory = player.inventory
    total_w = len(inventory) * (slot_size+padding)-padding
    start_x = config.screen_w//2-total_w//2
    y = config.screen_h - slot_size - 20

    for i, block in enumerate(inventory):
        x = start_x + i * (slot_size + padding)

        glDisable(GL_TEXTURE_2D)
        if i == inventory.selected_index:
            glColor4f(1, 1, 1, 0.9)
        else:
            glColor4f(0, 0, 0, 0.35)
        glBegin(GL_QUADS)
        glVertex2f(x - 2, y - 2)
        glVertex2f(x + slot_size + 2, y - 2)
        glVertex2f(x + slot_size + 2, y + slot_size + 2)
        glVertex2f(x - 2, y + slot_size + 2)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures[block])
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + slot_size, y)
        glTexCoord2f(1, 0); glVertex2f(x + slot_size, y + slot_size)
        glTexCoord2f(0, 0); glVertex2f(x, y + slot_size)
        glEnd()

    glDisable(GL_BLEND)
    _end_2d_overlay()

def draw_world(world,textures,from_blocks):
    from .blocks import water
    from .meshing import draw_chunk_block

    glDisable(GL_BLEND)
    for chunk in world.chunks.values():
        for block in from_blocks:
            draw_chunk_block(chunk,block,textures[block])

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1,1,1,0.75)
    for chunk in world.chunks.values():
        draw_chunk_block(chunk,water,textures[water])
    glColor4f(1,1,1,1)
    glDisable(GL_BLEND)
