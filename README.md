
<img width="1277" height="747" alt="image" src="https://github.com/user-attachments/assets/6fc144b9-6312-4666-a5db-1961ca4a24b0" />

# Actions:

Movement -> WASD

Jump -> Space

L Shift -> Submerge (not applicable currently)

Left Click -> Break

Right Click -> Place (Buggy)

Scroll -> Change block 

# Stack:

- Python 3.12
- OpenGL library
- Numpy library
- Pygame library
- Built-ins

# Voxel Engine

<img width="1270" height="670" alt="Screenshot 2026-07-21 020626" src="https://github.com/user-attachments/assets/fd676f57-21f1-4699-8d03-f047e0fc7ebb" />

For those who want a one liner -> I made a Minecraft copy.

Ok so, if I have your attention now, let's begin..

### Featuring the endless theme for the ysws program **Alchemize**

I started out this project for shipping in the season 1 of Alchemise, the ysws from Hackclub. Since my project fits well in the endless theme - that is it's endless terrain generation, it was a fantastic opportunity for me to take part in the program. 

**We all have played minecraft, haven't we?** If not, perhaps we have none the less seen or heard about it. It is a video game where we are able to witness the magic of procedural generation. Now how exactly does minecraft keeps on generating new chunks everytime a person renders it? This question kept knocking at my door, until I decided to make a voxel engine myself. Voxels are cubes represented by x,y and z coordinates in a 3 dimensional plane. Minecraft is made up of these voxels and the engine that generates these voxels is made using the heart of my project *the perlin noise algorithm*. This algorithm makes chaos look beatifull by adding patterns to it. We set the frequencies and then this algorithm makes modern procedural generation possible. Let's dive deeper into what perlin noise actually is! 

### The problem Perlin Noise solves ->

We need a height function $h(x, z)$ over the infinite $xz$-plane such that:

- it's **deterministic** the same $(x,z)$ always gives the same height, so
  chunks generated independently still fit together seamlessly at their
  borders,
- it's **continuous and smooth**  neighbouring columns have similar
  heights, so terrain doesn't look like random static,
- it's **not periodic or grid-aligned** in an obvious way real terrain
  doesn't look like a repeating tile,
- and it's **cheap to evaluate per-column**, since a world can have
  thousands of columns generated per second while chunks stream in.

A naive approach  e.g. $h(x,z) = \text{hash}(x,z) \bmod N$ is
deterministic and cheap, but produces pure noise with no spatial
coherence: every adjacent column would be uncorrelated, giving jagged,
unnatural spikes instead of hills. Perlin noise is the classic solution:
pseudo-random *gradients* fixed at integer lattice points, smoothly
interpolated in between.

### 2. Gradient lattice

Fix a pseudo-random unit gradient vector $\mathbf{g}_{i,j} \in \mathbb{R}^2$
at every integer lattice point $(i, j) \in \mathbb{Z}^2$:

$$
\mathbf{g}_{i,j} = \big(\cos\theta_{i,j},\ \sin\theta_{i,j}\big), \qquad
\theta_{i,j} \sim \mathcal{U}(0, 2\pi)
$$

In code, this is `PerlinNoise2D.__init__`: 256 random angles are drawn once
from a seeded RNG and stored as unit vectors in `self.gradients`. A
lattice point's gradient is looked up (not recomputed) via a **permutation
table** `self.perm` a shuffled array of $0\ldots255$, duplicated, indexed
as:

$$
\text{grad}(i,j) \;=\; \mathbf{g}_{\,P\big[(P[i \bmod 256] + j) \bmod 256\big] \bmod 256}
$$

where $P$ is the permutation table. This hashes any integer pair $(i,j)$
down to one of 256 fixed gradient vectors, deterministically and without
storing an infinite lattice, this is exactly `_gradient_at`.


### 3. Noise at an arbitrary point

For a query point $(x, y)$ (the engine's `noise(x, y)` uses `y` for what is
world-space $z$), let

$$
x_0 = \lfloor x \rfloor,\quad y_0 = \lfloor y \rfloor,\quad
x_1 = x_0+1,\quad y_1 = y_0+1
$$

be the four surrounding lattice corners, and let

$$
s_x = x - x_0, \qquad s_y = y - y_0
$$

be the point's fractional offset inside that cell (`sx`, `sy` in the
code). At each of the four corners $(x_c, y_c)$, take the dot product of
that corner's fixed gradient with the **offset vector** from the corner to
the query point:

$$
n_{c} = \mathbf{g}_{x_c,y_c} \cdot \big(x - x_c,\; y - y_c\big),
\qquad c \in \{00, 10, 01, 11\}
$$

This is precisely `n00, n10, n01, n11` in `noise()`, each is
`np.dot(self._gradient_at(...), [x - x_c, y - y_c])`. This dot product is
what makes it *gradient* noise: it's zero exactly at the corner itself
(offset vector is $\mathbf 0$) and grows as you move away from a corner in
the direction its gradient points, and shrinks moving away from it.


### 4. Smooth interpolation (the fade curve)

Linearly interpolating $n_{00}, n_{10}, n_{01}, n_{11}$ directly would
produce visible creases at lattice boundaries (discontinuous derivatives).
Perlin's fix is to interpolate using a smoothstep-like **fade function**
instead of the raw offset:

$$
f(t) = 6t^5 - 15t^4 + 10t^3
$$

which is exactly `_fade`: `t*t*t*(t*(t*6 - 15) + 10)`. This is the unique
quintic with $f(0)=0,\ f(1)=1,\ f'(0)=f'(1)=0,\ f''(0)=f''(1)=0$ it and
its first *and* second derivatives vanish at the cell boundaries, so the
resulting noise field is $C^2$-continuous: no visible seams between
lattice cells, which is what makes the terrain read as rolling hills
rather than a tiled grid.

Bilinear interpolation using the faded weights $u = f(s_x)$, $v = f(s_y)$
then gives the final scalar noise value:

$$
\begin{aligned}
n_{x0} &= (1-u)\,n_{00} + u\,n_{10} \\
n_{x1} &= (1-u)\,n_{01} + u\,n_{11} \\
\text{noise}(x,y) &= (1-v)\,n_{x0} + v\,n_{x1}
\end{aligned}
$$

 exactly `nx0`, `nx1`, and the function's return value.

### 5. Fractal (multi-octave) noise

A single noise layer looks smooth but repetitive at one spatial frequency, fine for gentle rolling hills, but not for terrain with both broad
valleys *and* fine detail. `fractal()` sums several **octaves** of the
same noise function at increasing frequency and decreasing amplitude:

$$
N(x,y) = \frac{1}{\sum_{k=0}^{O-1} p^{\,k}}
\sum_{k=0}^{O-1} p^{\,k} \cdot \text{noise}\!\left(\frac{x\, l^{\,k}}{s},\; \frac{y\, l^{\,k}}{s}\right)
$$

where $O$ is the octave count, $p$ the persistence (amplitude falloff per
octave), $l$ the lacunarity (frequency growth per octave), and $s$ an
overall scale. In the engine's default call, $O=4,\ p=0.5,\ l=2.0,\ s=48$
— each successive octave has half the amplitude and twice the frequency of
the previous one, and the whole thing is normalized by the sum of
amplitudes $\sum p^k$ so the result stays in $[-1, 1]$ regardless of
octave count. This is `fractal()`'s accumulator loop exactly.


### 6. From noise to voxel height

Finally, `height_at` maps the normalized fractal value into an integer
block height:

$$
h(w_x, w_z) = \text{clamp}\Big(1,\ H_{\text{world}}-8,\ \
H_{\text{base}} + \left\lfloor \left(\tfrac{N(w_x,w_z)}{2} + \tfrac12\right) A \right\rfloor \Big)
$$

where $N \in [-1,1]$ is remapped to $[0,1]$, scaled by amplitude $A$
(`terrain_amplitude`), offset by a base height $H_{\text{base}}$
(`terrain_base`), and clamped so terrain never pokes through the world's
vertical bounds. This single scalar height is what `Chunk.generate()`
consumes to decide, per column, how many dirt/grass blocks to stack and
where the water table sits.

## Assets:

For the assets I just searched up stuff like - grass block, dirt block etc and it all were just 5 images all along (ref - minecraft). I've set up a fallback system with colour codes provided. 

**Note:- the LaTeX notations were generated via an LLM**

Thank you

- Chinmoy
