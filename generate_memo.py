from Cube.cube import Cube

cube = Cube(can_parity_swap=False)

corners = ['A', 'B', 'U', 'D', 'J', 'F', 'G', 'H', 'E', 'I', 'K', 'L', 'X', 'N', 'O', 'P', 'R', 'M', 'S', 'T', 'C', 'V',
           'W', 'Z']
edges = ['A', 'U', 'B', 'D', 'E', 'F', 'G', 'H', 'M', 'J', 'I', 'L', 'K', 'N', 'O', 'P', 'Z', 'R', 'S', 'T', 'C', 'V',
         'W', 'X']

# {'A': 'A', 'B': 'B', 'U': 'U', 'D': 'D', 'J': 'J', 'F': 'F', 'G': 'G', 'H': 'H', 'E': 'E', 'I': 'I', 'K': 'K', 'L': 'L', 'X': 'X', 'N': 'N', 'O': 'O', 'P': 'P', 'R': 'R', 'M': 'M', 'S': 'S', 'T': 'T', 'C': 'C', 'V': 'V', 'W': 'W', 'Z': 'Z'}
# {'A': 'A', 'U': 'U', 'B': 'B', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'M': 'M', 'J': 'J', 'I': 'I', 'L': 'L', 'K': 'K', 'N': 'N', 'O': 'O', 'P': 'P', 'Z': 'Z', 'R': 'R', 'S': 'S', 'T': 'T', 'C': 'C', 'V': 'V', 'W': 'W', 'X': 'X'}


# will need to convert letter memo (ABC) to side representation (UDFB)

# how to scramble the cube properly idk
# by swapping the pieces literally, manually by reassigning the location of the letters ?!

# HOW TO E.G.

# buffer = 'A'
# cycle_from_buffer = 'VL'

buffer = 'L'
cycle_from_buffer = 'VX'

edges = cube.edge_swaps
print(edges)
# FROM edge_float_generator
import get_scrambles
from Cube.cube import Cube
from solution import Solution

# how to prevent a case like this
# F' U' B2 L2 B2 L2 U L2 U2 F2 L2 D' L F2 U F' D U' R' F U
"""
Not sure what this is supposed to do like 
generate a scramble that has a specific float in it or something
"""
floating_buffer = 'J'
number = 0
no_cycle_break_corner_memo = set()
print('Running...')
strict = False
while True:
    scramble = get_scrambles.get_scramble()
    cube = Cube(scramble)
    solution = Solution(scramble)
    buffers = solution.edge_float_buffers
    if floating_buffer in buffers:
        print(scramble)

    # print(scramble)

"""
D' F2 D2 B L2 F2 U2 R2 F2 U2 L2 B R D2 L U2 B R2 D' U' L'
buffers ['J', 'D', 'B']
B2 D' R2 D L' D F' R F B U' B2 U2 B2 D2 R2 F2 R2 U' B2
U' B' F' L2 F' U2 B U2 F' R2 B D' R' U' B D' B F L
U' F U F2 B R' D' L D' F2 R2 D' B2 R2 U R2 L2 D2 L'
L2 B R2 B2 F' D2 B L2 R2 D2 F' U' R' B2 D' B' U' L' D2 L' U'
R2 U2 B R2 B' R L U' F2 R' B2 D2 R2 D2 R F2 R B2 R
U2 B' L' F R' F B2 R' U F2 D' B2 D' F2 D R2 U2 D L

"""
