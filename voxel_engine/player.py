import math
from pygame.locals import K_w,K_s,K_a,K_d,K_SPACE,K_LSHIFT
from . import config
from .blocks import air,water
from .inventory import Inventory
from .noise import height_at

class Player:
    def __init__(self, world,x,z):
        self.world = world
        h = height_at(int(x), int(z))
        self.pos = [x,max(h+3,config.sea_level + 3),z]
        self.vel = [0.0,0.0,0.0]
        self.yaw = 0.0
        self.pitch = 0.0
        self.on_ground = False
        self.in_water = False
        self.inventory = Inventory()

    @property
    def selected_block(self):
        return self.inventory.selected_block
    
    @property
    def selected_slot(self):
        return self.inventory.selected_index
    
    @selected_slot.setter
    def selected_slot(self,index):
        self.inventory.select_index(index)

    def forward_vector(self):
        yaw_r = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)
        x = math.cos(pitch_r) * math.sin(yaw_r)
        y = math.sin(pitch_r)
        z = -math.cos(pitch_r) * math.cos(yaw_r)
        return (x,y,z)
    
    def eye_pos(self):
        return (self.pos[0],self.pos[1] + config.player_eye,self.pos[2])
    
    def _feet_in_water(self):
        bx = int(math.floor(self.pos[0]))
        by = int(math.floor(self.pos[1]))
        bz = int(math.floor(self.pos[2]))
        return self.world.get_block(bx,by,bz) == water

    def _aabb_collides(self,x,y,z):

        r = config.player_radius
        x0, x1 = x - r, x + r
        z0, z1 = z - r, z + r
        y0, y1 = y, y + config.player_height

        bx0, bx1 = int(math.floor(x0)), int(math.floor(x1))
        bz0, bz1 = int(math.floor(z0)), int(math.floor(z1))
        by0, by1 = int(math.floor(y0)), int(math.floor(y1-1e-4))

        for bx in range(bx0, bx1 + 1):
            for by in range(by0,by1+1):
                for bz in range(bz0,bz1 +1):
                    block = self.world.get_block(bx,by,bz)
                    if block != air and block != water:
                        return True
        return False
    
    def _compute_move_intent(self,keys):

        forward_yaw = math.radians(self.yaw)
        move_x = 0.0
        move_z = 0.0
        speed = config.swim_speed if self.in_water else config.walk_speed

        if keys[K_w]:
            move_x += math.sin(forward_yaw)
            move_z += -math.cos(forward_yaw)
        if keys[K_s]:
            move_x -= math.sin(forward_yaw)
            move_z -= -math.cos(forward_yaw)
        if keys[K_a]:
            move_x += math.sin(forward_yaw-math.pi/2)
            move_z += -math.cos(forward_yaw-math.pi/2)            
        if keys[K_d]:
            move_x += math.sin(forward_yaw+math.pi/2)
            move_z += -math.cos(forward_yaw+math.pi/2)    

        mag = math.hypot(move_x,move_z)
        if mag > 0:
            move_x = move_x/mag*speed
            move_z = move_z/mag*speed
        return move_x,move_z

    def _apply_vertical_input(self,dt,keys):
        if self.in_water:
            self.vel[1] *= config.water_vertical_damping
            if keys[K_SPACE]:
                self.vel[1] = config.swim_speed
            elif keys[K_LSHIFT]:
                self.vel[1] = -config.swim_speed
            else:
                self.vel[1] -= config.water_sink_acceleration*dt

        else:
            self.vel[1] -= config.gravity * dt
            if keys[K_SPACE] and self.on_ground:
                self.vel[1] = config.jump_speed

    def update(self,dt,keys):
        self.in_water = self._feet_in_water()

        move_x, move_z = self._compute_move_intent(keys)
        self._apply_vertical_input(dt, keys)

        new_x = self.pos[0] + move_x * dt
        if not self._aabb_collides(new_x,self.pos[1],self.pos[2]):
            self.pos[0] = new_x
        new_z = self.pos[2] + move_z * dt
        if not self._aabb_collides(self.pos[0],self.pos[1],new_z):
            self.pos[2] = new_z

        new_y = self.pos[1] + self.vel[1] *dt
        self.on_ground = False
        if self.vel[1] < 0:
            if self._aabb_collides(self.pos[0],new_y,self.pos[2]):
                self.pos[1] = math.floor(self.pos[1])
                self.vel[1] = 0
                self.on_ground = True
            else:
                self.pos[1] = new_y
        else:
            if self._aabb_collides(self.pos[0],new_y,self.pos[2]):
                self.vel[1] = 0
            else:
                self.pos[1] = new_y

        if self.pos[1] < -20:
            self.pos[1] = config.world_height + 5
            self.vel[1] = 0













