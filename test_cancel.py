from drill_generator import cancel, parallel_cancel
# from drill_generator import ColoredCube, invert_solution
# import kociemba
# print("Setup:", "U2 R F2 B'||", "B U2 F' U B2 U' F R2 U B2 D R2 D L2 D' B2 D'")
# print("Result:", cancel("U2 R F2 B'", "B U2 F' U B2 U' F R2 U B2 D R2 D L2 D' B2 D'"))
# from drill_generator import generate_premoves
import random

# print('yes')
#
# print(cancel("B'", "B2 D F2 D' B D' B2 R2 B2 D2 F2 L2 D' B2 U'"))
# print('done')
# quit()

# // R D B' L || L' B2 L B2 L' D' R' B' U B2 U' B2 U' B2
#   R D B L B2 L' D' R' B' U B2 U' B2 U' B2


# F D U2 || U2 D2 F U' F' D F U F2 R2 U2 R2 U' R2 U' R2 U'

# sol = ""
# post_move = "R L"
# k_sol = "R L"
post_move = "F' D2 R'"
k_sol = "R D2 F2 R2 F' U' B U' B U' L2 F2 U' R2 U F2 D' L2 U'"
# alg = "U R U R2' D' R U R' D R2 U2' R'"
# cube = ColoredCube(alg + " " + post_move)

# k_sol = "U2 D2 F U' F' D F U F2 R2 U2 R2 U' R2 U' R2 U'"  # kociemba.solve(cube.get_faces_colors())

# print("Result Before:", post_move, "||", k_sol)
print("Result:\t\t", cancel(post_move, k_sol))
# print("Result:\t\t", parallel_cancel(post_move.split(), k_sol.split()))

# the post move becomes the inverted premove
# from Cube.cube import Cube
#
# cube = Cube("U", can_parity_swap=False)
# cube.display_cube()
#
