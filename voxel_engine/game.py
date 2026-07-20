import pygame as py
from pygame.locals import (
    DOUBLEBUF,OPENGL,QUIT,KEYDOWN,MOUSEWHEEL,MOUSEBUTTONDOWN,K_ESCAPE,K_1,K_2,K_3,K_4,K_5 
)
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear
from . import config
from .blocks import air,water,placeable_blocks
from .world import World
from .player import Player
from .raycast import raycast
from .textures import load_all_textures
from . import renderer

_opaque_draw_order = [b for b in placeable_blocks if b!=water]
_slot_keys = {K_1: 0, K_2: 1, K_3: 2, K_4: 3, K_5: 4}

class Game:
    def __init__(self):
        py.init()
        py.display.set_mode((config.screen_w,config.screen_h),DOUBLEBUF|OPENGL)
        py.display.set_caption("Voxel Engine: Minecraft")
        py.mouse.set_visible(False)
        py.event.set_grab(True)

        self.clock = py.time.Clock()
        renderer.setup_gl()
        renderer.set_persepective()
        self.textures = load_all_textures()

        self.world = World()
        spawn_x, spawn_z = 0.5,0.5
        self.world.ensure_chunks_around(spawn_x,spawn_z)
        self.player = Player(self.wordl,spawn_x,spawn_z)

        self.mouse_captured = True
        self.running = True

    def handle_events(self):
        for event in py.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                self._handle_keydown(event)
            elif event.type == MOUSEWHEEL:
                self.player.inventory.scroll(-event.y)
            elif event.type == MOUSEBUTTONDOWN and self.mouse_captured:
                self._handle_mouse_click(event)

    def _handle_keydown(self,event):
        if event.key == K_ESCAPE:
            self.mouse_captured = not self.mouse_captured
            py.event.set_grab(self.mouse_captured)
            py.mouse.set_visible(not self.mouse_captured)
        elif event.key in _slot_keys:
            self.player.inventory.selected_index(_slot_keys[event.key])

    def _handle_mouse_click(self,event):
        if self.mouse_captured:
            mdx, mdy = py.mouse.get_rel()
            self.player.yaw += mdx * config.mouse_sensitivity
            self.player.ptich -= mdy * config.mouse_sensitivity
            self.player.pitch = max(-config.max_pitch, min(config.max_pitch, self.player.pitch))
        else:
            py.mouse.get_rel()

    def update(self,dt):
        self._handle_mouse_click(self)
        keys = py.key.get_pressed
        self.player.update(dt,keys)
        self.world.ensure_chunks_around(self.player.pos[0],self.player.pos[2])

    def _rebuild_dirty_meshes(self):
        from . meshing import upload_chunk_meshes_by_block
        rebuilt = 0
        for chunk in self.world.chunks.values():
            if chunk.mesh_dirty:
                upload_chunk_meshes_by_block(chunk,self.world)
                rebuilt += 1
                if rebuilt >= config.max_chunk_rebuilds_per_frame:
                    break

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        renderer.apply_camera(self.player)
        renderer.draw_world(self.world, self.textures, -_opaque_draw_order)
        renderer.draw_crosshair()
        renderer.draw_hotbar
        py.display.flip()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(config.target_fps)/1000.0,0.1)
            self.handle_events()
            self.update(dt)
            self.render()
        py.quit()

def main():
    Game().run()