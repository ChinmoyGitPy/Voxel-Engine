import math
import random
import numpy as np

from . import config

class PerlinNoise2D:

    def __init__(self,seed=0):
        rng = random.Random(seed)
        perm = list(range(256))
        rng.shuffle(perm)
        self.perm = np.array(perm+perm,dtype=np.int32)

        angles = [rng.uniform(0,2*math.pi) for _ in range(256)]
        self.gradients = np.array([[math.cos(a),math.sin(a)] for a in angles])

    @staticmethod
    def _fade(t):
        return t*t*t*(t*(t*6-15) + 10)
    
    def _gradient_at(self, ix,iy):
        idx = self.perm[(self.perm[ix & 255] + iy) & 255] & 255
        return self.gradients[idx]
    
    def noise(self,x,y):
        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1

        sx = x - x0
        sy = y - y0

        n00 = np.dot(self._gradient_at(x0,y0),[x-x0,y-y0])
        n10 = np.dot(self._gradient_at(x1,y0),[x-x1,y-y0])
        n01 = np.dot(self._gradient_at(x0,y1),[x-x0,y-y1])
        n11 = np.dot(self._gradient_at(x1,y1),[x-x1,y-y1])

        u = self._fade(sx)
        v = self._fade(sy)

        nx0 = n00*(1-u) + n10 * u
        nx1 = n01 * (1-u) + n11 * u
        return nx0 *(1-v) + nx1 * v
    
    def fractal(self,x,y,octaves=4,persistence=0.5,lacunarity=2.0,scale=1.0):
        amplitude = 1.0
        frequency = 1.0
        total = 0.0
        max_amp = 0.0
        for _ in range(octaves):
            total += self.noise(x*frequency/scale,y*frequency/scale)*amplitude
            max_amp += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total/max_amp if max_amp > 0 else 0.0
_terrain_noise = PerlinNoise2D(seed=config.noise_seed)

def height_at(wx,wz):
    n = _terrain_noise.fractal(wx,wz, octaves=4,persistence=0.5, lacunarity=2.0,scale=48.0)
    h = config.terrain_base + int((n * 0.5 + 0.5) * config.terrain_amplitude)
    return max(1,min(config.world_height-8,h))
