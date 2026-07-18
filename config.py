import os

screen_width, screen_h = 1280,720
fov = 70
near_plane,far_plane = 0.1, 400.0
target_fps = 60

chunk_size = 16
world_height = 48
render_distance = 5

sea_level = 14
terrain_base = 10
terrain_amplitude = 14

noise_seed = 67
tree_seed = 2026
tree_chance = 0.02

gravity = 24.0
jump_speed = 8.5
walk_speed = 5.2
swim_speed = 3.8
water_vertical_damping = 0.85
water_sink_acceleration = gravity * 0.15
mouse_sensitivity = 0.15
player_height = 1.7
player_eye = 1.6
player_radius = 0.3
max_pitch = 89

reach = 6.0

max_chunk_rebuilds_per_frame = 4
chunk_unload_margin = 1

asset_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)

sky_colour = (0.55, 0.75, 0.95,1.0)
fog_start_chunks = render_distance - 1.5
fog_end_chunks = render_distance

