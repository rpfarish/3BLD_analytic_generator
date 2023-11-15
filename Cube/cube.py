import json
from collections import deque

import dlin
import kociemba

from Cube.letterscheme import LetterScheme
from comms import COMMS

DEBUG = True


# TODO does not reorient the cube after scrambling.
class Cube:
    def __init__(self, s="", can_parity_swap=False, auto_scramble=True, ls=None, buffers=None, parity_swap_edges=None,
                 buffer_order=None):

        self.scramble = s.rstrip('\n').strip().split()
        self.has_parity = (len(self.scramble) - s.count('2')) % 2 == 1
        self.kociemba_order = 'URFDLB'
        self.kociemba_solved_cube = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        self.faces = 'ULFRBD'
        use_default_letter_scheme = True if ls is None else False
        if type(ls) is LetterScheme:
            self.ls = ls
        else:
            self.ls = ls = LetterScheme(ls, use_default=use_default_letter_scheme)

        self.slices = 'MSE'

        self.directions = ["", "'", "2"]
        self.opp_faces = {'U': 'D', 'D': 'U',
                          'F': 'B', 'B': 'F',
                          'L': 'R', 'R': 'L',
                          }

        # letter scheme
        UB, UR, UF, UL = ls['UB'], ls['UR'], ls['UF'], ls['UL']
        LU, LF, LD, LB = ls['LU'], ls['LF'], ls['LD'], ls['LB']
        FU, FR, FD, FL = ls['FU'], ls['FR'], ls['FD'], ls['FL']
        RU, RB, RD, RF = ls['RU'], ls['RB'], ls['RD'], ls['RF']
        BU, BL, BD, BR = ls['BU'], ls['BL'], ls['BD'], ls['BR']
        DF, DR, DB, DL = ls['DF'], ls['DR'], ls['DB'], ls['DL']

        UBL, UBR, UFR, UFL = ls['UBL'], ls['UBR'], ls['UFR'], ls['UFL']
        LUB, LUF, LDF, LDB = ls['LUB'], ls['LUF'], ls['LDF'], ls['LDB']
        FUL, FUR, FDR, FDL = ls['FUL'], ls['FUR'], ls['FDR'], ls['FDL']
        RUF, RUB, RDB, RDF = ls['RUF'], ls['RUB'], ls['RDB'], ls['RDF']
        BUR, BUL, BDL, BDR = ls['BUR'], ls['BUL'], ls['BDL'], ls['BDR']
        DFL, DFR, DBR, DBL = ls['DFL'], ls['DFR'], ls['DBR'], ls['DBL']

        if buffers is not None:
            self.default_edge_buffer = ls[buffers['edge_buffer']]
            self.default_corner_buffer = ls[buffers['corner_buffer']]
        else:
            self.default_edge_buffer = ls['UF']
            self.default_corner_buffer = ls['UFR']

        self.edge_memo_buffers = set()
        self.corner_memo_buffers = set()  # {UFR, RUF, FUR}

        self.corner_cycle_break_order = [UBR, UBL, UFL, RDF, RDB, LDF, LDB]
        self.edge_cycle_break_order = [UB, UR, UL, DF, FR, FL, DR, DL, BR, BL]

        if buffer_order is not None:
            self.buffer_order = buffer_order
            self.corner_buffer_order = [ls[buffer] for buffer in buffer_order['corners']]
            self.edge_buffer_order = [ls[buffer] for buffer in buffer_order['edges']]
        else:
            self.corner_buffer_order = [UFR, UBR, UBL, UFL, RDF, RDB]
            self.edge_buffer_order = [UF, UB, UR, UL, DF, DB, FR, FL, DR, DL]

        self.U_edges = deque([UB, UR, UF, UL])
        self.L_edges = deque([LU, LF, LD, LB])
        self.F_edges = deque([FU, FR, FD, FL])
        self.R_edges = deque([RU, RB, RD, RF])
        self.B_edges = deque([BU, BL, BD, BR])
        self.D_edges = deque([DF, DR, DB, DL])

        self.U_corners = deque([UBL, UBR, UFR, UFL])
        self.L_corners = deque([LUB, LUF, LDF, LDB])
        self.F_corners = deque([FUL, FUR, FDR, FDL])
        self.R_corners = deque([RUF, RUB, RDB, RDF])
        self.B_corners = deque([BUR, BUL, BDL, BDR])
        self.D_corners = deque([DFL, DFR, DBR, DBL])

        self.default_edges = self.U_edges + self.L_edges + self.F_edges + self.R_edges + self.B_edges + self.D_edges
        self.default_corners = (self.U_corners + self.L_corners + self.F_corners +
                                self.R_corners + self.B_corners + self.D_corners)

        self.adj_edges = {
            self.U_edges[0]: self.B_edges[0],
            self.U_edges[1]: self.R_edges[0],
            self.U_edges[2]: self.F_edges[0],
            self.U_edges[3]: self.L_edges[0],

            self.L_edges[0]: self.U_edges[3],
            self.L_edges[1]: self.F_edges[3],
            self.L_edges[2]: self.D_edges[3],
            self.L_edges[3]: self.B_edges[1],

            self.F_edges[0]: self.U_edges[2],
            self.F_edges[1]: self.R_edges[3],
            self.F_edges[2]: self.D_edges[0],
            self.F_edges[3]: self.L_edges[1],

            self.R_edges[0]: self.U_edges[1],
            self.R_edges[1]: self.B_edges[3],
            self.R_edges[2]: self.D_edges[1],
            self.R_edges[3]: self.F_edges[1],

            self.B_edges[0]: self.U_edges[0],
            self.B_edges[1]: self.L_edges[3],
            self.B_edges[2]: self.D_edges[2],
            self.B_edges[3]: self.R_edges[1],

            self.D_edges[0]: self.F_edges[2],
            self.D_edges[1]: self.R_edges[2],
            self.D_edges[2]: self.B_edges[2],
            self.D_edges[3]: self.L_edges[2],
        }

        self.adj_corners = {
            self.U_corners[0]: [self.B_corners[1], self.L_corners[0]],
            self.U_corners[1]: [self.R_corners[1], self.B_corners[0]],
            self.U_corners[2]: [self.F_corners[1], self.R_corners[0]],
            self.U_corners[3]: [self.L_corners[1], self.F_corners[0]],

            self.L_corners[0]: [self.U_corners[0], self.B_corners[1]],
            self.L_corners[1]: [self.F_corners[0], self.U_corners[3]],
            self.L_corners[2]: [self.D_corners[0], self.F_corners[3]],
            self.L_corners[3]: [self.B_corners[2], self.D_corners[3]],

            self.F_corners[0]: [self.U_corners[3], self.L_corners[1]],
            self.F_corners[1]: [self.R_corners[0], self.U_corners[2]],
            self.F_corners[2]: [self.D_corners[1], self.R_corners[3]],
            self.F_corners[3]: [self.L_corners[2], self.D_corners[0]],

            self.R_corners[0]: [self.U_corners[2], self.F_corners[1]],
            self.R_corners[1]: [self.B_corners[0], self.U_corners[1]],
            self.R_corners[2]: [self.D_corners[2], self.B_corners[3]],
            self.R_corners[3]: [self.F_corners[2], self.D_corners[1]],

            self.B_corners[0]: [self.U_corners[1], self.R_corners[1]],
            self.B_corners[1]: [self.L_corners[0], self.U_corners[0]],
            self.B_corners[2]: [self.D_corners[3], self.L_corners[3]],
            self.B_corners[3]: [self.R_corners[2], self.D_corners[2]],

            self.D_corners[0]: [self.F_corners[3], self.L_corners[2]],
            self.D_corners[1]: [self.R_corners[3], self.F_corners[2]],
            self.D_corners[2]: [self.B_corners[3], self.R_corners[2]],
            self.D_corners[3]: [self.L_corners[3], self.B_corners[2]],

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

        self.u_adj_edges_index = [0, 0, 0, 0]
        self.r_adj_edges_index = [1, 3, 1, 1]
        self.l_adj_edges_index = [3, 3, 3, 1]
        self.f_adj_edges_index = [2, 3, 0, 1]
        self.b_adj_edges_index = [0, 3, 2, 1]
        self.d_adj_edges_index = [2, 2, 2, 2]

        self.u_adj_corners_index = [(1, 0), (1, 0), (1, 0), (1, 0)]
        self.r_adj_corners_index = [(2, 1), (0, 3), (2, 1), (2, 1)]
        self.l_adj_corners_index = [(0, 3), (0, 3), (0, 3), (2, 1)]
        self.f_adj_corners_index = [(3, 2), (0, 3), (1, 0), (2, 1)]
        self.b_adj_corners_index = [(1, 0), (0, 3), (3, 2), (2, 1)]
        self.d_adj_corners_index = [(3, 2), (3, 2), (3, 2), (3, 2)]

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
            "'2": 2,
            "": 1,
            "3": -1,
            "3'": 1,
            -1: "'",
            1: "",
            2: "2",
            -2: "2",
            "''": 1,
        }

        # UF-UR swap
        if can_parity_swap:
            self.parity_swap(parity_swap_edges)

        if auto_scramble:
            self.scramble_cube()

    # memo
    def parity_swap(self, parity_swap_edges="UF-UR"):
        if not self.has_parity:
            return

        if parity_swap_edges == "UF-UR" or parity_swap_edges is None:
            self.U_edges[1], self.U_edges[2] = self.U_edges[2], self.U_edges[1]
            self.F_edges[0], self.R_edges[0] = self.R_edges[0], self.F_edges[0]
        elif parity_swap_edges == "UL-UB":
            self.U_edges[0], self.U_edges[3] = self.U_edges[3], self.U_edges[0]
            self.B_edges[0], self.L_edges[0] = self.L_edges[0], self.B_edges[0]

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        for (edges, corners), (edges2, corners2) in zip(self.cube_faces().values(), other.cube_faces().values()):
            if edges != edges2 or corners != corners2:
                return False
        else:
            return True

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        else:
            return not result

    def do_move(self, move: str):
        has_wide_move = False
        if not move:
            return

        elif len(move) > 3:
            raise ValueError("Invalid move length", move)

        rotation = self.rotations_map[move[1:]]

        moves_map = {
            'U': (self.U_edges, self.u_adj_edges, self.u_adj_edges_index,
                  self.U_corners, self.u_adj_corners, self.u_adj_corners_index),

            'R': (self.R_edges, self.r_adj_edges, self.r_adj_edges_index,
                  self.R_corners, self.r_adj_corners, self.r_adj_corners_index),

            'L': (self.L_edges, self.l_adj_edges, self.l_adj_edges_index,
                  self.L_corners, self.l_adj_corners, self.l_adj_corners_index),

            'F': (self.F_edges, self.f_adj_edges, self.f_adj_edges_index,
                  self.F_corners, self.f_adj_corners, self.f_adj_corners_index),

            'B': (self.B_edges, self.b_adj_edges, self.b_adj_edges_index,
                  self.B_corners, self.b_adj_corners, self.b_adj_corners_index),

            'D': (self.D_edges, self.d_adj_edges, self.d_adj_edges_index,
                  self.D_corners, self.d_adj_corners, self.d_adj_corners_index),

            'M': ([self.U_edges, self.F_edges, self.D_edges, self.B_edges],
                  [self.F_edges, self.D_edges, self.B_edges, self.U_edges],
                  self.m_edges_index, self.m_adj_edges_index),

            'S': ([self.U_edges, self.R_edges, self.D_edges, self.L_edges],
                  [self.R_edges, self.D_edges, self.L_edges, self.U_edges],
                  self.s_edges_index, self.s_adj_edges_index),

            'E': ([self.F_edges, self.R_edges, self.B_edges, self.L_edges],
                  [self.R_edges, self.B_edges, self.L_edges, self.F_edges],
                  self.e_edges_index, self.e_adj_edges_index),
        }

        face_turn = move[:1]

        if face_turn in self.faces:
            side = moves_map.get(face_turn)
            self._rotate_layer(rotation, *side)
        elif face_turn in self.slices:
            side = moves_map.get(face_turn)
            self._rotate_slice(rotation, *side)
        elif face_turn.islower():
            self._rotate_wide(move)

    @staticmethod
    def _rotate_layer(rotation, edges, adj_edges, adj_edges_index, corners, adj_corners, adj_corners_index):

        edges.rotate(rotation)
        corners.rotate(rotation)

        # rotate adjacent of the side edges
        side = deque([i[j] for i, j in zip(adj_edges, adj_edges_index)])
        side.rotate(rotation)
        for adj_side_obj, adj_edges_index, side_slice in zip(adj_edges, adj_edges_index, side):
            adj_side_obj[adj_edges_index] = side_slice

        # rotate adjacent of the side corners
        side = deque([(layer[i], layer[j]) for layer, (i, j) in zip(adj_corners, adj_corners_index)])
        side.rotate(rotation)
        for adj_side_obj, (i, j), (a, b) in zip(adj_corners, adj_corners_index, side):
            adj_side_obj[i] = a
            adj_side_obj[j] = b

    @staticmethod
    def _rotate_slice(rotation, edges, adj_edges, edges_index, adj_edges_index):
        # rotate UF L following M slice
        side = deque([edge[i] for edge, i in zip(edges, edges_index)])
        side.rotate(rotation)
        for s, edge, edges_index in zip(side, edges, edges_index):
            edge[edges_index] = s

        side = deque([edge[i] for edge, i in zip(adj_edges, adj_edges_index)])
        side.rotate(rotation)
        for s, edge, edges_index in zip(side, adj_edges, adj_edges_index):
            edge[edges_index] = s

    def _rotate_wide(self, face_turn):
        self.do_move(face_turn.upper())
        slice_, direction = self.wide_moves[face_turn[:1]]
        rotation = self.rotations_map[face_turn[1:]]
        rotation *= direction
        slice_turn = slice_[:1] + self.rotations_map[rotation]
        self.do_move(slice_turn)

    @property
    def solved_corners(self):
        return [default for default, current in zip(self.default_corners, self.all_corners)
                if default == current and default != self.default_corner_buffer
                and default not in self.adj_corners[self.default_corner_buffer]
                ]

    @property
    def twisted_corners(self):
        return {default: current for default, current in zip(self.default_corners, self.all_corners)
                if default in self.adj_corners[current] and default != self.default_corner_buffer
                and default not in self.adj_corners[self.default_corner_buffer]
                }

    @property
    def twisted_corners_count(self):
        return len(self.twisted_corners) // 3

    @property
    def solved_edges(self):
        return [default for default, current in zip(self.default_edges, self.all_edges)
                if default == current and default != self.default_edge_buffer
                and default != self.adj_edges[self.default_edge_buffer]
                ]

    @property
    def flipped_edges(self):
        return {default: current for default, current in zip(self.default_edges, self.all_edges)
                if default == self.adj_edges[current] and default != self.default_edge_buffer
                and default != self.adj_edges[self.default_edge_buffer]
                }

    @property
    def all_edges(self):
        return self.U_edges + self.L_edges + self.F_edges + self.R_edges + self.B_edges + self.D_edges

    @property
    def all_corners(self):
        return self.U_corners + self.L_corners + self.F_corners + self.R_corners + self.B_corners + self.D_corners

    @property
    def edge_swaps(self):
        solved = self.solved_edges
        flipped = self.flipped_edges
        return {
            default: current
            for default, current in zip(self.default_edges, self.all_edges)
            if default not in solved and default not in flipped
        }

    @property
    def corner_swaps(self):
        solved = self.solved_corners
        twisted = self.twisted_corners
        return {
            default: current
            for default, current in zip(self.default_corners, self.all_corners)
            if current not in solved and current not in twisted
        }

    def cube_faces(self):
        all_edges = [self.U_edges, self.L_edges, self.F_edges, self.R_edges, self.B_edges, self.D_edges]
        all_corners = [self.U_corners, self.L_corners, self.F_corners, self.R_corners, self.B_corners, self.D_corners]
        return {face: pieces for face, *pieces in zip(self.faces, all_edges, all_corners)}

    def display_cube(self):
        for name, (e, c) in self.cube_faces().items():
            print('-------', name, '-------')
            print(f'      {c[0]} {e[0]} {c[1]}     ')
            print(f'      {e[3]}   {e[1]}      ')
            print(f'      {c[3]} {e[2]} {c[2]}   \n')

    def scramble_cube(self, scramble=None):
        if scramble is None:
            scramble = self.scramble
        else:
            scramble = scramble.rstrip('\n').strip().split()

        for move in scramble:
            self.do_move(move)

    def is_solved(self):
        if self == Cube():
            return True
        return False

    def scramble_edges_from_memo(self, memo, edge_buffer=None):
        edge_buffer = self.default_edge_buffer if edge_buffer is None else edge_buffer
        iter_memo = iter(memo)
        self._reset()
        for target in iter_memo:
            a = str(target)
            b = str(next(iter_memo))
            buffer = COMMS[str(edge_buffer)]
            comm = buffer[a][b]
            self.scramble_cube(comm)

        return self.solve()

    def scramble_corners_from_memo(self, memo, corner_buffer=None):
        corner_buffer = self.default_corner_buffer if corner_buffer is None else corner_buffer
        iter_memo = iter(memo)
        self._reset()
        for target in iter_memo:
            a = str(target)
            b = str(next(iter_memo))
            buffer = COMMS[str(corner_buffer)]
            comm = buffer[a][b]
            self.scramble_cube(comm)

        return self.solve()

    def _reset(self):
        self.__init__()

    def get_faces_colors(self):
        cube_faces = self.cube_faces()
        cube_string = ""
        for face_name in self.kociemba_order:
            e, c = cube_faces.get(face_name)
            face = c[0][0] + e[0][0] + c[1][0]
            face += e[3][0] + face_name + e[1][0]
            face += c[3][0] + e[2][0] + c[2][0]
            cube_string += face
        return cube_string

    def get_dlin_trace(self):
        return dlin.trace(" ".join(self.scramble))

    def solve(self, max_depth=20, invert=False):
        # todo fix this to accept both letter schemes
        if not self.ls.is_default:
            raise Exception("letter scheme must be default in order to solve cube")
        if not invert:
            return kociemba.solve(self.get_faces_colors(), max_depth=max_depth)
        else:
            return kociemba.solve(self.kociemba_solved_cube, self.get_faces_colors(), max_depth=max_depth)


if __name__ == "__main__":
    with open("../settings.json") as f:
        settings = json.loads(f.read())
        letter_scheme = settings['letter_scheme']
    #     buffers = settings['buffers']
    # # s = "F2 D2 R' D2 F2 R2 U2 B2 L2 R B' U' R F' D R U' B' D' L"
    # scram = "L' R B U2 B' L2 R2 F2 L' R U' F2 U'"
    # # s = "R U' D'  R' U R  D2 R' U' R D2 D U R'"
    #
    # print(Cube("B R L B' U B2 F2 R F D2 B' R2 U2 D B F D F L' U2 B D' R2").twisted_corners_count)
    scramble = "R U R' U' " * 5
    cube = Cube(scramble)
    print(scramble)
    # # print(c.adj_corners)
    # cube.display_cube()
    print(cube.get_faces_colors())
    print(cube.solve(invert=False))
    print(cube.solve(invert=True))
    # # # todo adapt for different versions of FDR ie FRD
    # # # c.drill_corner_sticker('FDR')
    # # # todo letter scheme for below is a dependency for working
    # # c.drill_edge_buffer("DF")
