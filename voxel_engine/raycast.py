import math

from . import config
from .blocks import air

def raycast(world,origin,direction,max_dist=config.reach):

    x,y,z = origin
    dx,dy,dz = direction
    ix,iy,iz = math.floor(x),math.floor(y),math.floor(z)
    step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
    step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
    step_z = 1 if dz > 0 else (-1 if dz < 0 else 0)

    def t_max(pos,ipos,step,d):
        if d == 0:
            return math.inf
        if step > 0:
            return (ipos + 1 - pos)/d
        return (pos-ipos)/(-d)
    
    def t_delta(step,d):
        if d == 0:
            return math.inf
        return abs(1.0/d)
    
    tmax_x = t_max(x,ix,step_x,dx)
    tmax_y = t_max(y,iy,step_y,dy)
    tmax_z = t_max(z,iz,step_z,dz)

    tdelta_x = t_delta(x,ix,step_x,dx)
    tdelta_y = t_delta(y,iy,step_y,dy)
    tdelta_z = t_delta(z,iz,step_z,dz)

    last_normal = (0,0,0)
    traveled = 0.0

    while traveled <= max_dist:
        block = world.get_blocks(ix,iy,iz)
        if block != air:
            hit = (ix,iy,iz)
            place = (ix-last_normal[0],iy-last_normal[1],iz-last_normal[2])
            return hit,place,last_normal
        
        if tmax_x < tmax_y and tmax_x < tmax_z:
            ix += step_x
            traveled = tmax_x
            tmax_x = tdelta_x
            last_normal = (-step_x,0,0)
        elif tmax_y < tmax_z:
            iy += step_y
            traveled = tmax_y
            tmax_y += tdelta_y
            last_normal = (0,-step_y,0)
        else:
            iz += step_z
            traveled = tmax_z
            tmax_z += tdelta_z
            last_normal = (0,0 -step_z)

    return None,None,None
