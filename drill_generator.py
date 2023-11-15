import random
from collections import deque
from itertools import combinations, product, chain

import kociemba

from Cube.cube import Cube
from get_scrambles import gen_premove

DEBUG = 0

# U Face
UB = 'U'
UR = 'U'
UF = 'U'
UL = 'U'

# L Face
LU = 'L'
LF = 'L'
LD = 'L'
LB = 'L'

# F Face
FU = 'F'
FR = 'F'
FD = 'F'
FL = 'F'

# R Face
RU = 'R'
RB = 'R'
RD = 'R'
RF = 'R'

# B Face
BU = 'B'
BL = 'B'
BD = 'B'
BR = 'B'

# D Face
DF = 'D'
DR = 'D'
DB = 'D'
DL = 'D'

# -------CORNERS--------

# U Face
UBL = 'U'
UBR = 'U'
UFR = 'U'
UFL = 'U'

# L Face
LUB = 'L'
LUF = 'L'
LDF = 'L'
LDB = 'L'

# F Face
FUL = 'F'
FUR = 'F'
FDR = 'F'
FDL = 'F'

# R Face
RUF = 'R'
RUB = 'R'
RDB = 'R'
RDF = 'R'

# B Face
BUR = 'B'
BUL = 'B'
BDL = 'B'
BDR = 'B'

# D Face
DFL = 'D'
DFR = 'D'
DBR = 'D'
DBL = 'D'

# -----BUFFERS------
EDGE_BUFFER = UF
CORNER_BUFFER = UFR


# TODO move to drill in Cube

# noinspection PyMissingConstructor
class ColoredCube(Cube):
    def __init__(self, s=""):
        self.scramble = s.rstrip('\n').strip().split(' ')[:]
        self.faces = "ULFRBD"
        self.kociemba_order = "URFDLB"
        self.slices = 'MSE'

        self.default_edge_buffer = EDGE_BUFFER
        self.default_corner_buffer = CORNER_BUFFER
        self.edge_memo_buffers = set()
        self.corner_memo_buffers = set()

        self.corner_buffer_order = [UBR, UBL, UFL, RDF, RDB, LDF, LDB]
        self.edge_buffer_order = [UB, UR, UL, DF, FR, FL, DR, DL]

        double_turns = [move for move in self.scramble if move.endswith('2')]
        self.has_parity = (len(self.scramble) - len(double_turns)) % 2 == 1

        self.U_corners = deque([UBL, UBR, UFR, UFL])
        self.L_corners = deque([LUB, LUF, LDF, LDB])
        self.F_corners = deque([FUL, FUR, FDR, FDL])
        self.R_corners = deque([RUF, RUB, RDB, RDF])
        self.B_corners = deque([BUR, BUL, BDL, BDR])
        self.D_corners = deque([DFL, DFR, DBR, DBL])

        self.U_edges = deque([UB, UR, UF, UL])
        self.L_edges = deque([LU, LF, LD, LB])
        self.F_edges = deque([FU, FR, FD, FL])
        self.R_edges = deque([RU, RB, RD, RF])
        self.B_edges = deque([BU, BL, BD, BR])
        self.D_edges = deque([DF, DR, DB, DL])

        self.default_edges = self.U_edges + self.L_edges + self.F_edges + self.R_edges + self.B_edges + self.D_edges
        self.default_corners = (self.U_corners + self.L_corners + self.F_corners +
                                self.R_corners + self.B_corners + self.D_corners)
        self.adj_edges = {
            UB: BU, UR: RU, UL: LU, FL: LF, DL: LD,
            BL: LB, FR: RF, BR: RB, DR: RD, DF: FD,
            DB: BD, BU: UB, RU: UR, LU: UL, LF: FL,
            LD: DL, LB: BL, RF: FR, RB: BR, RD: DR,
            FD: DF, BD: DB, UF: FU, FU: UF
        }

        self.adj_corners = {
            UBL: BUL + LUB, UBR: RUB + BUR, UFR: FUR + RUF, UFL: LUF + FUL,
            LUB: UBL + BUL, LUF: FUL + UFL, LDF: DFL + FDL, LDB: BDL + DBL,
            FUL: UFL + LUF, FUR: RUF + UFR, FDR: DFR + RDF, FDL: LDF + DFL,
            RUF: UFR + FUR, RUB: BUR + UBR, RDB: DBR + BDR, RDF: FDR + DFR,
            BUR: UBR + RUB, BUL: LUB + UBL, BDL: DBL + LDB, BDR: RDB + DBR,
            DFL: FDL + LDF, DFR: RDF + FDR, DBR: BDR + RDB, DBL: LDB + BDL
        }

        self.u_adj_edges = [self.B_edges, self.R_edges, self.F_edges, self.L_edges]
        self.r_adj_edges = [self.U_edges, self.B_edges, self.D_edges, self.F_edges]
        self.l_adj_edges = [self.U_edges, self.F_edges, self.D_edges, self.B_edges]
        self.f_adj_edges = [self.U_edges, self.R_edges, self.D_edges, self.L_edges]
        self.b_adj_edges = [self.U_edges, self.L_edges, self.D_edges, self.R_edges]
        self.d_adj_edges = [self.F_edges, self.R_edges, self.B_edges, self.L_edges]

        self.u_adj_corners = [self.B_corners, self.R_corners, self.F_corners, self.L_corners]
        self.r_adj_corners = [self.U_corners, self.B_corners, self.D_corners, self.F_corners]
        self.l_adj_corners = [self.U_corners, self.F_corners, self.D_corners, self.B_corners]
        self.f_adj_corners = [self.U_corners, self.R_corners, self.D_corners, self.L_corners]
        self.b_adj_corners = [self.U_corners, self.L_corners, self.D_corners, self.R_corners]
        self.d_adj_corners = [self.F_corners, self.R_corners, self.B_corners, self.L_corners]

        self.u_adj_corners_index = [(1, 0), (1, 0), (1, 0), (1, 0)]
        self.r_adj_corners_index = [(2, 1), (0, 3), (2, 1), (2, 1)]
        self.l_adj_corners_index = [(0, 3), (0, 3), (0, 3), (2, 1)]
        self.f_adj_corners_index = [(3, 2), (0, 3), (1, 0), (2, 1)]
        self.b_adj_corners_index = [(1, 0), (0, 3), (3, 2), (2, 1)]
        self.d_adj_corners_index = [(3, 2), (3, 2), (3, 2), (3, 2)]

        self.u_adj_edges_index = [0, 0, 0, 0]
        self.r_adj_edges_index = [1, 3, 1, 1]
        self.l_adj_edges_index = [3, 3, 3, 1]
        self.f_adj_edges_index = [2, 3, 0, 1]
        self.b_adj_edges_index = [0, 3, 2, 1]
        self.d_adj_edges_index = [2, 2, 2, 2]

        # Starting from UF following L
        self.m_edges_index = [2, 2, 2, 0]
        self.m_adj_edges_index = [0, 0, 2, 0]
        # Starting from UR following F
        self.s_edges_index = [1, 2, 3, 0]
        self.s_adj_edges_index = [0, 1, 2, 3]
        # Starting from FR following D
        self.e_edges_index = [1, 1, 1, 1]
        self.e_adj_edges_index = [3, 3, 3, 3]

        self.wide_moves = {
            'u': ("E", -1),
            'r': ('M', -1),
            'f': ('S', 1),
            'l': ('M', 1),
            'd': ('E', 1),
            'b': ('S', -1),
        }
        self.rotations_map = {
            "'": -1,
            "2": 2,
            "2'": 2,
            "": 1,
            "3": -1,
            "3'": 1,
            -1: "'",
            1: "",
            2: "2",
            -2: "2",
        }

        self.scramble_cube()

    def get_faces_colors(self):
        cube_faces = self.cube_faces()
        cube_string = ""
        for face_name in self.kociemba_order:
            e, c = cube_faces.get(face_name)
            face = c[0] + e[0] + c[1]
            face += e[3] + face_name + e[1]
            face += c[3] + e[2] + c[2]
            cube_string += face
        return cube_string

    def display_cube(self):
        for name, (e, c) in self.cube_faces().items():
            print('-------', name, '-------')
            print(f'      {c[0]} {e[0]} {c[1]}     ')
            print(f'      {e[3]} {name} {e[1]}     ')
            print(f'      {c[3]} {e[2]} {c[2]}   \n')


def invert_solution(s: str) -> str:
    s = s.rstrip('\n').strip().split(' ')[:]
    inverse = []
    for move in reversed(s):
        if move.endswith("'"):
            inverse.append(move.strip("'"))
        elif move.endswith("2"):
            inverse.append(move)
        else:
            inverse.append(move + "'")
    return " ".join(inverse)


def parallel_cancel(pre_move: list, solution: list):
    s = solution.copy()
    pre_move_len = len(pre_move)

    solution = pre_move + solution
    # todo figure out why this is needed
    # post_move = "F' D2 R'"
    # k_sol = "R D2 F2 R2 F' U' B U' B U' L2 F2 U' R2 U F2 D' L2 U'"
    if '' in solution:
        solution.remove('')
    opp = {'U': 'D', 'D': 'U',
           'F': 'B', 'B': 'F',
           'L': 'R', 'R': 'L',
           }
    for i in range(len(solution) - 3):
        if DEBUG: print("SOLUTION", solution)
        first_layer = solution[i][0]
        first_turn = solution[i]
        second_layer = solution[i + 1][0]
        third_layer = solution[i + 2][0]
        third_turn = solution[i + 2]
        if first_layer == third_layer and first_layer == opp[second_layer]:
            canceled_cube = ColoredCube(first_turn + " " + third_turn)
            # todo convert to using combined rotation and simplifying
            kociemba_solution = canceled_cube.solve(invert=True).split()
            if DEBUG: print('k sol', kociemba_solution)

            if i < pre_move_len:
                pre_move[i] = " ".join(kociemba_solution)
            if i + 2 < pre_move_len:
                pre_move[i + 2] = ''

            if i >= pre_move_len:
                s[i - pre_move_len] = kociemba_solution
            if i + 2 >= pre_move_len:
                s[i + 2 - pre_move_len] = ''
            if DEBUG: print(pre_move)
            if DEBUG: print(solution)
            if '' in pre_move:
                pre_move.remove('')
            if '' in s:
                s.remove('')

            return parallel_cancel(pre_move, s)
            # kociemba_solution

    return pre_move, s


def cancel(pre_move, solution):
    # todo find a way to also cancel U D U moves
    # aka check for parallel cancellations
    solution = solution.rstrip('\n').strip().split(' ')[:]
    pre_move = pre_move.rstrip('\n').strip().split(' ')[:]
    # checking for parallel cancel
    pre_move, solution = parallel_cancel(pre_move, solution)
    rev_premove = pre_move[::-1]
    if DEBUG: print(solution, pre_move, rev_premove, sep=" || ")
    solved = ColoredCube()

    # full vs partial cancel

    # calculate cancel type
    for depth, (pre, s) in enumerate(zip(rev_premove.copy(), solution.copy())):
        combined = pre + " " + s
        canceled_cube = ColoredCube(combined)

        if DEBUG: print(pre, "||", s, "Full cancel:", "nope" if solved != canceled_cube else "yep")

        if not pre or not s:
            break

        if DEBUG: print(pre, "||", s, "Parital cancel:", "nope" if pre[0] != s[0] else "yep")

        if solved == canceled_cube and depth < 1:
            # full cancel
            # remove the two canceled moves and recurse
            if DEBUG: print('recursing')
            rev_premove.remove(pre)
            solution.remove(s)
            if DEBUG: print(solution, rev_premove, sep=" || ")

            return cancel(" ".join(rev_premove[::-1]), " ".join(solution))

        # partial cancel
        elif pre[0] == s[0] and depth < 1:
            canceled_cube = ColoredCube(pre + " " + s)
            # todo convert to using combined rotation and simplifying
            kociemba_solution = invert_solution(canceled_cube.solve()).split()
            if DEBUG: print('k sol', kociemba_solution)

            # kociemba_solution
            if DEBUG: print(rev_premove)
            rev_premove.remove(pre)
            solution.remove(s)
            solution = kociemba_solution + solution
            return cancel(" ".join(rev_premove[::-1]), " ".join(solution))
        break
    if DEBUG: print("Returning", " ".join(rev_premove[::-1]), " ".join(solution), sep=" || ")
    return " ".join(rev_premove[::-1]) + " " + " ".join(solution).strip()


# if partial cancel return simplified version


# if full cancel return removed full cancel and recurse


def main(mode):
    twists = {
        "CW": {
            "UBL": "R U R D R' D' R D R' U' R D' R' D R D' R2",
            "UBR": "R D R' D' R D R' U' R D' R' D R D' R' U",
            "UFL": "U' R' D R D' R' D R U R' D' R D R' D' R",
            "DFL": "U R U' R' D R U R' U' R U R' D' R U' R'",
            "DFR": "D' U' R' D R U R' D' R D R' D' R U' R' D R U",
            "DBR": "U R U' R' D' R U R' U' R U R' D R U' R'",
            "DBL": "D' R D R' U' R D' R' D R D' R' U R D R'"
        },
        "CCW": {
            "UBL": "R2 D R' D' R D R' U R D' R' D R D' R' U' R'",
            "UBR": "U' R D R' D' R D R' U R D' R' D R D' R'",
            "UFL": "R' D R D' R' D R U' R' D' R D R' D' R U",
            "DFL": "R U R' D R U' R' U R U' R' D' R U R' U'",
            "DFR": "U' R' D' R U R' D R D' R' D R U' R' D' R U D",
            "DBR": "R U R' D' R U' R' U R U' R' D R U R' U'",
            "DBL": "R D' R' U' R D R' D' R D R' U R D' R' D",
        }
    }

    algs_help_num = 0
    algs_help = []
    # algs = [
    #     # LTLC UBL C
    #     "U R U R2' D' R U R' D R2 U2' R'",
    #     "R' D' R U R' D R2 U' R' U R U R' U' R U R' U",
    #     "U' R' U2 R U R2' D' R U R' D R2 U2'",
    #     "U R U R' U R2 D R' U' R D' R' U' R'",
    #     "R' D R' U R D' R' U R2 U' R2' U' R2 U'",
    #     "U R' D' R U R' D R2 U R' U2 R U R' U'",
    #     # LTLC UBL CC
    #
    #     "U' R D R' U' R D' R2' U R U' R' U' R U R' U' R",
    #     "U2 R' U' R2 D R' U' R D' R2' U2' R U",
    #     "R U R D R' U R D' R2' U' R U' R' U'",
    #     "U' R U' R' U R U' R' U' R U R2' D' R U' R' D R",
    #     "U R U' R' U2 R U' R2' D' R U' R' D R U'",
    #     "R U2 R' U' R2 D R' U' R D' R2' U'",
    #     # LTLC UFL C
    #     "U' R2 D R' U' R D' R' U' R' U R U R' U2",
    #     "U R U R' U2 L U' R U L' U R'",
    #     "U2' R' U2 L U' R U L' U R' U R U'",
    #     "R' U' R U D' R U' R U R U' R2' D U",
    #     "U R U R' U' R U R2' D' R U2 R' D R2 U2' R' U",
    #     "U' R' U' R U R' U' R2 D R' U R D' R' U2 R' U R U'",
    #
    #     # LTLC UFL CC
    #     "U R' U' R U2 R D R' U' R D' R2' U R U' R' U R U",
    #     "D' U' R2 U R' U' R' U R' U' D R' U R",
    #     "U2 R U' R' U' R U R D R' U R D' R2' U",
    #     "U' R' U L' U R2 U R2' U R2 U2' R' L",
    #     "U2 R2 D' r U2 r' D R U2 R U'",
    #     "U' L' U' L U' R U' L' U R' U2' L",
    #     # LTCT UBR C
    #     "R2 U R' D' R U R' D R' U' R2 U' R2' U'",
    #     "D R2' U' R U R U' R D' U R U' R' U",
    #     "U R' D' R U' R' D R U2 R U R' U2 R U R' U'",
    #     "U' R' U2 R U R2' F' R U R U' R' F R U'",
    #     "U' f R' F' R U2 R U2' R' U2 S'",
    #     "U R' U R U R' U' R' D' R U' R' D R2",
    # ]
    # algs = ["U R' U' R U2 R D R' U' R D' R2' U R U' R' U R U",
    # "D R2' U' R U R U' R D' U R U' R' U", "U' R' U2 R U R2' F' R U R U' R' F R U'"]
    algs = [
        "D2 R2' D' R2 U R2' D R2 D' R2' U' R2 D'",
        "D R2' D' R2 U R2' D R2 D' R2 U' R2'",
        "R2' D' R2 U R2' D R2 D' R2' U' R2 D",
        "D R2' U R2 D R2' D' R2 U' R2' D R2 D2'",
        "U' R2' D R2 U R2' U' R2 D' R2' U R2",
        "R2 U R2' D R2 D' R2' U' R2 D R2' D'",
        "U' R2' U R2 D' R2' U' R2 U R2' D R2",
        "D' R2' U R2 D R2' D' R2 U' R2' D R2",
        "R2' U' R2 D R2' U R2 U' R2' D' R2 U",
        "R2' D' R2 U' R2' U R2 D R2' U' R2 U",
    ]

    algs += [
        "D R2' D R2 U' R2' D' R2 D R2' U R2 D2'", "R2' D R2 U' R2' D' R2 D R2' U R2 D'",
        "D' R2' D R2 U' R2' D' R2 D R2' U R2", "D2' R2' D R2 U' R2' D' R2 D R2' U R2 D",
        "D2 R2' U' R2 D' R2' D R2 U R2' D' R2 D'", "R2' D R2 U R2' U' R2 D' R2' U R2 U'",
        "D R2' U' R2 D' R2' D R2 U R2' D' R2", "R2 U' R2' U R2 D R2' U' R2 U R2' D'",
        "R2' U R2 D' R2' U' R2 U R2' D R2 U'", "R2' U' R2 D' R2' D R2 U R2' D' R2 D",
        "U R2' U' R2 D R2' U R2 U' R2' D' R2", "D R2 U' R2' U R2 D' R2' U' R2 U R2'",
        "D' R2 U' R2' U R2 D R2' U' R2 U R2'", "D' R2' U' R2 D' R2' D R2 U R2' D' R2 D2",
        "U R2' D' R2 U' R2' U R2 D R2' U' R2", "R2 U' R2' U R2 D' R2' U' R2 U R2' D",
    ]
    # all ltct UU with some ltct UD

    two_flips = {
        "[U , R' E2 R2 E' R']": "U R' E2 R2 E' R' U' R E R2' E2' R",
        "[U' : [S , R' F' R]] [U2' , M']": "U' S R' F' R S' R' F R U' M' U2 M",
        "[U' , L E2' L2' E L]": "U' L E2' L2' E L U L' E' L2 E2 L'",
        "[L' E2' L , U'] [U' , L E' L']": "L' E2' L U' L' E2 L2 E' L' U L E L'",
        "[R E2 R' , U] [U , R' E R]": "R E2 R' U R E2' R2' E R U' R' E' R",
        "[R' E2 R , U] [U , R E' R']": "R' E2 R U R' E2' R2 E' R' U' R E R'",
        "[L E2' L' , U'] [U' , L' E L]": "L E2' L' U' L E2 L2' E L U L' E' L",
        "[M' , U2] [U : [S , R' F' R]]": "M' U2 M U' S R' F' R S' R' F R U'",
        "[U' : [R E R' , U2]] [U : [S , R2']]": "U' R E R' U2 R E' R' S R2' S' R2 U'",
        "[M U' : [S , R' F' R]] [M , U2]": "M U' S R' F' R S' R' F R U' M' U2'",
        "[U : [L' E' L , U2']] [U' : [S' , L2]]": "U L' E' L U2' L' E L S' L2 S L2' U",
        "[R' E2 R2 E' R' , U']": "R' E2 R2 E' R' U' R E R2' E2' R U",
        "[S , R' F' R] [U' : [M' , U2]]": "S R' F' R S' R' F R U' M' U2 M U'",
        "[U R : [U' , R' E' R2 E2 R']]": "U R U' R' E' R2 E2 R' U R E2' R2' E U'",
        "[U , R' E R] [R E2 R' , U]": "U R' E R U' R' E' R2 E2 R' U R E2' R' U'",
        "[R E' R2' : [F2 , R S' R']] [R : [E' , R2']]": "R E' R2' F2 R S' R' F2' R S R' E R",
        "[U : [L' E L , U]] [U2 : [L E2' L' , U']]": "U L' E L U L' E' L2 E2' L' U' L E2 L' U'",
        "[U' : [M' , U2]] [S , R' F' R]": "U' M' U2 M U' S R' F' R S' R' F R",
        "[R' F' R , S'] [S' U' : [M' , U2]]": "R' F' R S' R' F R U' M' U2 M U' S",
        "[U' M U' : [S , R' F' R]] [U' : [M , U2]]": "U' M U' S R' F' R S' R' F R U' M' U'",
        "[R2' , S'] [S' : [U2 , R E R']]": "R2' S' R2 U2 R E R' U2' R E' R' S",
        "[L E2' L2' E L , U]": "L E2' L2' E L U L' E' L2 E2 L' U'",
        "[L E' L' , U] [U , L' E2' L]": "L E' L' U L E L2' E2' L U' L' E2 L",
        "[R' E R , U'] [U' , R E2 R']": "R' E R U' R' E' R2 E2 R' U R E2' R'",
        "[R E' R' , U'] [U' , R' E2 R]": "R E' R' U' R E R2' E2 R U R' E2' R",
        "[L' E L , U] [U , L E2' L']": "L' E L U L' E' L2 E2' L' U' L E2 L'",
        "[U2 , M'] [U' : [S , R' F' R]]": "U2 M' U2' M U' S R' F' R S' R' F R U",
        "[U : [R E R' , U2]] [U' : [S , R2']]": "U R E R' U2 R E' R' S R2' S' R2 U",
        "[U2 M U' : [S , R' F' R]] [U2 , M]": "U2 M U' S R' F' R S' R' F R U' M'",
        "[U' : [L' E' L , U2']] [U : [S' , L2']]": "U' L' E' L U2' L' E L S' L2' S L2 U'",
        "[U' , L E' L'] [L' E2' L , U']": "U' L E' L' U L E L2' E2' L U' L' E2 L U",
        "[U' : [R' E R , U']] [U2' : [R E2 R' , U]]": "U' R' E R U' R' E' R2 E2 R' U R E2' R' U",
        "[U' : [R E' R' , U']] [U2' : [R' E2 R , U]]": "U' R E' R' U' R E R2' E2 R U R' E2' R U",
        "[L' E L2 : [F2' , L' S L]] [L' : [E , L2]]": "L' E L2 F2' L' S L F2 L' S' L E' L'",
        "[U : [M' , U2']] [S' , L F L']": "U M' U2' M U S' L F L' S L F' L'",
        "[S , R2'] [U2 , R E R']": "S R2' S' R2 U2 R E R' U2' R E' R'",
        "[U M U' : [S , R' F' R]] [U : [M , U2']]": "U M U' S R' F' R S' R' F R U' M' U",
        "[L F L' , S] [S U : [M' , U2']]": "L F L' S L F' L' U M' U2' M U S'",
        "[R S R' F2 : [R2 , E]] [R S R' , F2]": "R S R' F2 R2 E R2' E' R S' R' F2'",
        "[R2 , E'] [E' : [F2 , R S' R']]": "R2 E' R2' F2 R S' R' F2' R S R' E",
        "[R2 , E] [R S' R' , F2]": "R2 E R2' E' R S' R' F2 R S R' F2'",
        "[R U' : [M' , U2]] [R S R' , F']": "R U' M' U2 M U' S R' F' R S' R' F",
        "[S L : [E' , L2']] [r , E' L' E]": "S L E' L2' E L S' r E' L' E r' E' L E",
        "[M : [L' E2' L , U']] [M : [U' , L E' L']]": "M L' E2' L U' L' E2 L2 E' L' U L E L' M'",
        "[L : [E' , L2']] [L F2' L' , S]": "L E' L2' E L2 F2' L' S L F2 L' S'",
        "[L2' , E'] [L' S L , F2']": "L2' E' L2 E L' S L F2' L' S' L F2",
        "[E , R2] [F2 , R S' R']": "E R2 E' R2' F2 R S' R' F2' R S R'",
        "[M' : [R' E R , U']] [M' : [U' , R E2 R']]": "M' R' E R U' R' E' R2 E2 R' U R E2' R' M",
        "[R' : [E , R2]] [R' F2 R , S']": "R' E R2 E' R2' F2 R S' R' F2' R S",
        "[M : [R E2 R' , U]] [M : [U , R' E R]]": "M R E2 R' U R E2' R2' E R U' R' E' R M'",
        "[S' R' : [E , R2]] [l' , E R E']": "S' R' E R2 E' R' S l' E R E' l E R' E'",
        "[R2' , E'] [E' R' : [S' , R' F2 R]]": "R2' E' R S' R' F2 R S R' F2' R2 E",
        "[r : [E' , R' U' R]] [M' : [U' , R' E2 R]]": "r E' R' U' R E R' U R r' M' U' R' E2 R U R' E2' R M",
        "[l : [S , R2']] [l U2 l' , S']": "l S R2' S' R2 U2 l' S' l U2' l' S",
        "[r' : [E2 , R U R']] [M : [U , R E' R']]": "r' E2 R U R' E2' R U' R' r M U R E' R' U' R E R' M'",
        "[S' R : [E' , R2']] [l , E' R' E]": "S' R E' R2' E R S l E' R' E l' E' R E",
        "[R' U' : [M' , U2]] [R' : [S , R' F' R]]": "R' U' M' U2 M U' S R' F' R S' R' F R2",
        "[S L' : [E , L2]] [r' , E L E']": "S L' E L2 E' L' S' r' E L E' r E L' E'",
        "[l : [E2' , L' U' L]] [M : [U' , L' E L]]": "l E2' L' U' L E2 L' U L l' M U' L' E L U L' E' L M'",
        "[r' : [S' , L2]] [r' U2' r , S]": "r' S' L2 S L2' U2' r S r' U2 r S'",
        "[S , R F' R'] [S' , R' F' R]": "S R F' R' S' R F R' S' R' F' R S R' F R",
        "[M2 U' : [S , R' F' R]] [M2 : [U2 , M']]": "M2 U' S R' F' R S' R' F R U' M' U2' M'",
        "[S' , L' F L] [S , L F L']": "S' L' F L S L' F' L S L F L' S' L F' L'",
        "[S2' , r' U' r] [r' : [U' , L' E L]]": "S2' r' U' r S2 r' L' E L U L' E' L r",
        "[U' : [R2' , S']] [R F R' , S']": "U' R2' S' R2 S U R F R' S' R F' R' S",
        "[S2 , l U l'] [l : [U , R E' R']]": "S2 l U l' S2' l R E' R' U' R E R' l'",
    }

    if mode == "1":
        algs = [
            "U R U R2' D' R U R' D R2 U2' R'",
            "R' D' R U R' D R2 U' R' U R U R' U' R U R' U",
            "U' R' U2 R U R2' D' R U R' D R2 U2'",
            "U R U R' U R2 D R' U' R D' R' U' R'",
            "R' D R' U R D' R' U R2 U' R2' U' R2 U'",
            "U R' D' R U R' D R2 U R' U2 R U R' U'",
            "R2 U R' D' R U R' D R' U' R2 U' R2' U'",
            "D R2' U' R U R U' R D' U R U' R' U",
            "U R' D' R U' R' D R U2 R U R' U2 R U R' U'",
            "U' R' U2 R U R2' F' R U R U' R' F R U'",
            "U' f R' F' R U2 R U2' R' U2 S'",
            "U R' U R U R' U' R' D' R U' R' D R2",
            "U' R2 D R' U' R D' R' U' R' U R U R' U2",
            "U R U R' U2 L U' R U L' U R'",
            "U2' R' U2 L U' R U L' U R' U R U'",
            "R' U' R U D' R U' R U R U' R2' D U",
            "U R U R' U' R U R2' D' R U2 R' D R2 U2' R' U",
            "U' R' U' R U R' U' R2 D R' U R D' R' U2 R' U R U'",
            "U R D R' U R D' R2' U R U2 R' U R U'",
            "R D R' U R D' R2' U R U R' U2' R",
            "D U R2 D' R U R' D R2 U R' U2 R D'",
            "U' R D R' U' R D' R2' U R U' R' U' R U R' U' R",
            "U2 R' U' R2 D R' U' R D' R2' U2' R U",
            "R U R D R' U R D' R2' U' R U' R' U'",
            "U' R U' R' U R U' R' U' R U R2' D' R U' R' D R",
            "U R U' R' U2 R U' R2' D' R U' R' D R U'",
            "R U2 R' U' R2 D R' U' R D' R2' U'",
            "D' U R2 D' R U R' D R2 U R' U2 R D",
            "R2' D' R U R' D R U R U' R' U' R U'",
            "U R' F' R U R' U' R' F R2 U' R' U2 R U",
            "R U R' U' R U R2' D' R U' R' D R U2 R U' R' U2",
            "U R U2' R' U' F' R U R' U' R' F R2 U' R'",
            "U' R U R' U' R' U R' U' D R' U R D' R",
            "U R U' R' U2 R U' R' U2 R' D' R U R' D R U'",
            "U R' U' R U2 R D R' U' R D' R2' U R U' R' U R U",
            "D' U' R2 U R' U' R' U R' U' D R' U R",
            "U2 R U' R' U' R U R D R' U R D' R2' U",
            "U' R' U L' U R2 U R2' U R2 U2' R' L",
            "U2 R2 D' r U2 r' D R U2 R U'",
            "U' L' U' L U' R U' L' U R' U2' L",
            "D R' U2 R U' R2 D' R U' R' D R2 U' D'",
            "D U R' U' R U2 R' U' R2 D R' U' R D' R' U' D'",
            "R' U2 R U' R2 D' R U' R' D R2 U'",
            "U R' U' R U2 R' U' R2 D R' U' R D' R' U'",
            "D' R' U2 R U' R2 D' R U' R' D R2 U' D",
            "D' U R' U' R U2 R' U' R2 D R' U' R D' R' U' D",
        ]

    elif mode == "2":
        cw_twists = twists["CW"].values()
        ccw_twists = twists["CCW"].values()
        cw = list(combinations(cw_twists, r=2))
        ccw = list(combinations(ccw_twists, r=2))
        algs = [a + " " + b for (a, b) in cw + ccw]

    elif mode == "3":
        cw_twists = twists["CW"].values()
        ccw_twists = twists["CCW"].values()
        cw = list(combinations(cw_twists, r=3))
        ccw = list(combinations(ccw_twists, r=3))
        algs = [a + " " + b + " " + c for (a, b, c) in cw + ccw]

    elif mode == "4":
        algs = list(two_flips.values())
        random.shuffle(algs)
    elif mode == "5":
        cw_twists = twists["CW"].values()
        ccw_twists = twists["CCW"].values()

        algs = []
        for cw_twist, ccw_twist in product(cw_twists, ccw_twists):
            if not Cube(cw_twist + " " + ccw_twist).is_solved():
                algs.append(cw_twist + " " + ccw_twist)

        algs.extend(chain(cw_twists, ccw_twists))

    last_solution = None
    no_repeat = True
    num = 1
    len_algs = len(algs)
    # TODO support wide moves
    while True:
        if not algs:
            break
        if DEBUG: print("getting random alg...")
        alg = a = random.choice(algs)

        post_move = gen_premove()
        if DEBUG: print(post_move)

        alg_with_post_move = alg + " " + post_move
        cube = ColoredCube(alg_with_post_move)
        if DEBUG: print("kociemba solving...")

        k_sol = kociemba.solve(cube.get_faces_colors(), max_depth=16)

        if DEBUG:
            print("//", post_move, "||", k_sol)
            print("SETUP:", post_move, alg_with_post_move, sep=" || ")
            print("canceling")

        solution = cancel(post_move, k_sol)

        if len(solution.split()) > 25:
            if DEBUG:
                print(f"Long solution {len(solution.split())}:")
                continue

        if no_repeat:
            algs.remove(alg)

        if DEBUG: print("at input...")
        if last_solution != solution:
            print(f"Num {num}/{len_algs}:", solution)
            num += 1
            last_solution = solution
            response = input("")
            if response == 'quit':
                return
            elif response.startswith('a'):
                print("Alg:", a, '\n')
                algs_help_num += 1
                algs_help.append(a)
    print(algs_help_num, algs_help)


if __name__ == "__main__":
    main(mode=0)
