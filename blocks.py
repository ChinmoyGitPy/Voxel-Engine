air = 0
grass = 1
dirt = 2
wood = 3
leaves = 4
water = 5

solid_blocks = {grass,dirt,wood,leaves,water} #occupies physcial space
transparent_blocks = {air,water,leaves} #water and leaves are drawn 
placeable_blocks = {grass,dirt,wood,leaves,water}

block_names = {grass:"Grass",dirt:"Dirt",wood:"Wood",leaves:"Leaves",water:"Water"}
fallback_colours = {
    grass: (86, 156, 68),
    dirt: (110,76,48),
    wood: (117,84,46),
    leaves: (58,122,46),
    water:(46,96,180)
}

def is_solid(block):
    return block in solid_blocks

def is_placeable(block):
    return block in placeable_blocks

