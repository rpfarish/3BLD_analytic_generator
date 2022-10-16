import random
from collections import deque

import kociemba

import get_scrambles
from Cube.letterscheme import letter_scheme, LetterScheme
from comms import COMMS

DEBUG = True


# TODO does not reorient the cube after scrambling
class Cube:
    def __init__(self, s="", can_parity_swap=False, auto_scramble=True, ls=None, buffers=None):
        self.scramble = s.rstrip('\n').strip().split()
        self.faces = 'ULFRBD'
        use_default_letter_scheme = True if ls is None else False
        if type(ls) is LetterScheme:
            self.ls = ls
        else:
            self.ls = ls = LetterScheme(ls, use_default=use_default_letter_scheme)
        self.slices = 'MSE'
        self.kociemba_order = "URFDLB"
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
        self.corner_memo_buffers = {UFR, RUF, FUR}

        self.corner_buffer_order = [UBR, UBL, UFL, RDF, RDB, LDF, LDB]
        self.edge_buffer_order = [UB, UR, UL, DF, FR, FL, DR, DL]

        double_turns = [move for move in self.scramble if '2' in move]
        self.has_parity = (len(self.scramble) - len(double_turns)) % 2 == 1

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
        self.default_corners = self.U_corners + self.L_corners + self.F_corners + self.R_corners + self.B_corners + self.D_corners

        # todo if len of move is > 3 throw error'
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
            "": 1,
            "3": -1,
            "3'": 1,
            -1: "'",
            1: "",
            2: "2",
            -2: "2",
        }

        # UF-UR swap
        if self.has_parity and can_parity_swap:
            self.U_edges[1], self.U_edges[2] = self.U_edges[2], self.U_edges[1]
            self.F_edges[0], self.R_edges[0] = self.R_edges[0], self.F_edges[0]

        if auto_scramble:
            self.scramble_cube()

    def parity_swap(self):
        if self.has_parity:
            self.U_edges[1], self.U_edges[2] = self.U_edges[2], self.U_edges[1]
            self.F_edges[0], self.R_edges[0] = self.R_edges[0], self.F_edges[0]

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
        if not move:
            return

        elif len(move) > 3:
            raise ValueError("Invalid move length")

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
            print(f'      {e[3]}   {e[1]}          ')
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

    def get_new_corner_buffer(self, avail_moves):
        for new_buffer in self.corner_buffer_order:
            if new_buffer in avail_moves:
                return new_buffer
        else:
            return random.choice(list(avail_moves))

    def memo_corners(self):
        curr = buffer = self.default_corner_buffer
        self.corner_memo_buffers.add(buffer)
        avail_moves = self.corner_swaps
        curr = avail_moves[curr]
        memo = []
        while avail_moves:
            new_memo = [curr]
            # Memo until a cycle break
            while True:
                curr = avail_moves[curr]
                new_memo.append(curr)
                if curr == buffer or curr in self.adj_corners[buffer]:
                    break

            # Remove memo and adj from avail
            for i in new_memo:
                if i in avail_moves:
                    avail_moves.pop(i)
                    for j in self.adj_corners[i]:
                        avail_moves.pop(j)

            # Remove buffer and adj from avail
            if buffer in avail_moves:
                avail_moves.pop(buffer)
                for i in self.adj_corners[buffer]:
                    avail_moves.pop(i)

            # Append the new memo onto the current memo
            memo += new_memo

            # Return the memo when avail is empty
            if not avail_moves:
                return [m for m in memo if m not in self.adj_corners[self.default_corner_buffer]
                        and m != self.default_corner_buffer]

            # Pick a new corner buffer
            curr = buffer = self.get_new_corner_buffer(avail_moves)
            self.corner_memo_buffers.add(buffer)

    def get_new_edge_buffer(self, avail_moves):
        # # todo also check the other side of the buffer piece at first
        for new_buffer in self.edge_buffer_order:
            if new_buffer in avail_moves:
                return new_buffer
        else:
            return random.choice(list(avail_moves))

    def memo_edges(self):
        buffer = self.default_edge_buffer
        avail_moves = self.edge_swaps
        def_buff = self.default_edge_buffer
        def_buff_adj = self.adj_edges[self.default_edge_buffer]
        self.edge_memo_buffers.add(buffer)
        curr = avail_moves[buffer]
        memo = []
        while avail_moves:
            new_memo = [curr]
            # Memo until a cycle break
            while True:
                curr = avail_moves[curr]
                if curr != self.default_edge_buffer and curr != self.adj_edges[self.default_edge_buffer]:
                    new_memo.append(curr)
                if curr == buffer or curr == self.adj_edges[buffer]:
                    break

            # Remove memo and adj from avail
            for move in new_memo:
                if move in avail_moves:
                    avail_moves.pop(move)
                    avail_moves.pop(self.adj_edges.get(move))

            # Remove buffer and adj from avail
            if buffer in avail_moves:
                avail_moves.pop(buffer)
                avail_moves.pop(self.adj_edges.get(buffer))

            # Append the new memo onto the current memo
            memo += new_memo

            # Return the memo when avail is empty
            if not avail_moves:
                return [letter for letter in memo if letter != def_buff and letter != def_buff_adj]

            # Pick a new edge buffer
            curr = buffer = self.get_new_edge_buffer(avail_moves)
            self.edge_memo_buffers.add(buffer)

    @staticmethod
    def format_edge_memo(memo):
        return ' '.join([f'{memo[i]}{memo[i + 1]}' for i in range(0, len(memo) - 1, 2)])

    def invert_solution(self, s=None) -> str:
        if type(s) is str:
            s = s.rstrip('\n').strip().split(' ')[:]
        elif s is None:
            s = self.scramble
        inverse = []
        for move in reversed(s):
            if move.endswith("'"):
                inverse.append(move.strip("'"))
            elif move.endswith("2"):
                inverse.append(move)
            else:
                inverse.append(move + "'")
        return " ".join(inverse)

    def format_corner_memo(self, memo):
        parity_target = memo.pop() if self.has_parity else ''
        memo = self.format_edge_memo(memo) + " " + parity_target
        return memo.strip()

    def get_solution(self, max_depth=24):
        return kociemba.solve(self.get_faces_colors(), max_depth=max_depth)

    def get_inverse_state_scramble(self, repeat_scramble=True):
        if repeat_scramble:
            return kociemba.solve(self.get_faces_colors())
        # GENERATE POST-MOVE
        # SOLVE STATE + POST-MOVE
        # UNDO POST-MOVE AND CANCEL SOLUTION

    def gen_premove(self, pre_move_len=3):

        turns = []
        scram_len = random.randint(1, pre_move_len)

        # first turn
        turn = random.choice(self.faces)
        direction = random.choice(self.directions)
        scramble = [turn + direction]
        turns.append(turn)

        for turn_num in range(1, scram_len):
            direction = random.choice(self.directions)
            last_turn = turns[turn_num - 1]
            while turn == last_turn or (
                    self.opp_faces[turn] == last_turn and turns[turn_num - 2] == self.opp_faces[last_turn]):
                turn = random.choice(self.faces)
            scramble.append(turn + direction)
            turns.append(turn)

        return " ".join(scramble)

    def scramble_edges_from_memo(self, memo, edge_buffer=None):
        edge_buffer = self.default_edge_buffer if edge_buffer is None else edge_buffer
        iter_memo = iter(memo)

        for target in iter_memo:
            a = str(target)
            b = str(next(iter_memo))
            buffer = COMMS[str(edge_buffer)]
            comm = buffer[a][b]
            self.scramble_cube(comm)

        sol = kociemba.solve(self.get_faces_colors())
        return sol

    def remove_irrelevant_edge_buffers(self, edges, edge_buffer):
        edges.pop(self.adj_edges[self.default_edge_buffer])
        edges.pop(self.default_edge_buffer)

        edge_buffer_order = self.edge_buffer_order.copy()
        for buff in edge_buffer_order:
            edges.pop(buff)
            edges.pop(self.adj_edges[buff])

            if buff == edge_buffer:
                break
        return edges

    def reduce_scramble(self, scramble=None):
        if scramble is None:
            scramble = " ".join(self.scramble)
        cube = Cube(scramble)
        reduced_scramble = cube.get_solution(max_depth=min(len(scramble.split()), 20))
        # print(len(scramble.split()), len(reduced_scramble.split()))
        return cube.invert_solution(reduced_scramble)

    def drill_edge_sticker(self, sticker_to_drill, single_cycle=True, return_list=False, cycles_to_exclude: set = None):
        from solution import Solution

        # todo support starting from any buffer
        # support default certain alternate pseudo edge swaps depending on last corner target
        scrambles = []
        all_edges = self.default_edges.copy()
        buffer = self.default_edge_buffer
        buffer_adj = self.adj_edges[buffer]
        all_edges.remove(buffer)
        all_edges.remove(buffer_adj)

        adj = self.adj_edges[sticker_to_drill]
        all_edges.remove(sticker_to_drill)
        all_edges.remove(adj)
        algs_to_drill = {sticker_to_drill + i for i in all_edges}
        number = 0

        if cycles_to_exclude is not None:
            algs_to_drill = algs_to_drill.difference(cycles_to_exclude)

        if single_cycle:
            frequency = 1
        else:
            frequency = int(input("Enter freq (recommended less than 3): "))

        no_repeat = True
        # I don't recommend going above 2 else it will take forever
        while len(algs_to_drill) >= frequency:
            scramble = get_scrambles.gen_premove(28, min_len=25)
            cube = Cube(scramble, can_parity_swap=True, ls=self.ls)
            edge_memo = cube.format_edge_memo(cube.memo_edges()).split(' ')
            no_cycle_break_edge_memo = set()
            last_added_pair = ''
            edge_buffers = cube.edge_memo_buffers
            for pair in edge_memo:
                pair_len_half = len(pair) // 2
                a = pair[:pair_len_half]
                b = pair[pair_len_half:]

                if a in edge_buffers or b in edge_buffers:
                    break
                last_added_pair = pair
                no_cycle_break_edge_memo.add(pair)

            # avoid missing a cycle due to breaking into a flipped edge
            if last_added_pair in algs_to_drill and (len(cube.flipped_edges) // 2) % 2 == 1:
                continue

            algs_in_scramble = algs_to_drill.intersection(no_cycle_break_edge_memo)
            if len(algs_in_scramble) >= frequency:
                if not return_list:
                    print("Scramble:", self.reduce_scramble(scramble))
                    # todo make it so if you're no_repeat then allow to repeat the letter pairs
                    response = input('Enter "r" to repeat letter pairs: ')
                    if response == 'm':
                        Solution(scramble).display()
                        scrambles.append(scramble)
                        response = input('Enter "r" to repeat letter pair(s): ')

                    if response != 'r' and no_repeat:
                        algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                    print()
                else:
                    algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                scrambles.append(scramble)
        if return_list:
            return scrambles

    def remove_piece(self, target_list, piece, ltr_scheme):
        piece_adj1, piece_adj2 = self.adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    def generate_random_pair(self, target_list, ltr_scheme):
        first = random.choice(target_list)
        self.remove_piece(target_list, first, ltr_scheme)
        second = random.choice(target_list)
        return first + second

    def generate_drill_list(self, piece_type, ltr_scheme: LetterScheme, buffer, target):
        # pick what letter scheme to use
        # how to separate c from e
        # just doing corners first
        all_targets = LetterScheme(use_default=False).get_edges()
        self.remove_piece(all_targets, buffer, ltr_scheme)

        # random_list = []
        # # generate random pair
        # for _ in range(18):
        #     target_list = all_targets[:]
        #     random_list.append(generate_random_pair(target_list, ltr_scheme))

        target_list = all_targets[:]
        # remove buffer stickers
        self.remove_piece(target_list, target, ltr_scheme)

        # generate random pairs
        # generate specific pairs
        # generate target groups e.g. just Z or H and k
        # generate inverse target groups
        # specify buffer
        return {target + i for i in target_list}

    def drill_corner_sticker(self, sticker_to_drill, single_cycle=True, return_list=False,
                             cycles_to_exclude: set = None):
        # from solution import Solution
        #
        # # todo support starting from any buffer
        # # support default certain alternate pseudo edge swaps depending on last corner target
        # scrambles = []
        #
        # all_corners = self.default_corners.copy()
        # buffer = self.default_corner_buffer
        # buffer_adj1, buffer_adj2 = self.adj_corners[buffer]
        # all_corners.remove(buffer)
        # all_corners.remove(buffer_adj1)
        # all_corners.remove(buffer_adj2)
        #
        # adj1, adj2 = self.adj_corners[sticker_to_drill]
        # all_corners.remove(sticker_to_drill)
        # all_corners.remove(adj1)
        # all_corners.remove(adj2)
        # algs_to_drill = {sticker_to_drill + i for i in all_corners}
        # number = 0
        #
        # if cycles_to_exclude is not None:
        #     algs_to_drill = algs_to_drill.difference(cycles_to_exclude)
        #
        # if single_cycle:
        #     frequency = 1
        # else:
        #     frequency = int(input("Enter freq (recommended less than 3): "))
        #
        # no_repeat = True
        # # I don't recommend going above 2 else it will take forever
        # while len(algs_to_drill) >= frequency:
        #     scramble = get_scrambles.gen_premove(28, min_len=25)
        #     cube = Cube(scramble, can_parity_swap=True, ls=self.ls)
        #     corner_memo = cube.format_corner_memo(cube.memo_corners()).split(' ')
        #     no_cycle_break_corner_memo = set()
        #     last_added_pair = ''
        #     corner_buffers = cube.corner_memo_buffers
        #     for pair in corner_memo:
        #         if len(pair) > 3:
        #             pair_len_half = len(pair) // 2
        #             a = pair[:pair_len_half]
        #             b = pair[pair_len_half:]
        #         elif not cycles_to_exclude:
        #             a = pair
        #             b = ''
        #         else:
        #             break
        #
        #         if a in corner_buffers or b in corner_buffers:
        #             break
        #         no_cycle_break_corner_memo.add(pair)
        #
        #     algs_in_scramble = algs_to_drill.intersection(no_cycle_break_corner_memo)
        #
        #     if len(algs_in_scramble) >= frequency:
        #         if not return_list:
        #             print("Scramble:", self.reduce_scramble(scramble))
        #             # todo make it so if you're no_repeat then allow to repeat the letter pairs
        #             response = input('Enter "r" to repeat letter pairs: ')
        #             if response == 'm':
        #                 Solution(scramble).display()
        #                 scrambles.append(scramble)
        #                 response = input('Enter "r" to repeat letter pair(s): ')
        #
        #             if response != 'r' and no_repeat:
        #                 algs_to_drill = algs_to_drill.difference(algs_in_scramble)
        #             print()
        #         else:
        #             algs_to_drill = algs_to_drill.difference(algs_in_scramble)
        #         scrambles.append(scramble)
        #
        # if return_list:
        #     return scrambles
        # todo fix buffer thing
        algs_to_drill = self.generate_drill_list('c', letter_scheme, "U", sticker_to_drill)
        number = 0

        alg_freq_dist = {str(pair): 0 for pair in algs_to_drill}
        # print(type(alg_freq_dist))
        # print('Running...')
        count = 2
        inc_amt = 2
        while True:
            scramble = get_scrambles.get_scramble()
            cube = Cube(scramble, ls=letter_scheme)
            corner_memo = cube.format_corner_memo(cube.memo_corners()).split(' ')
            no_cycle_break_corner_memo = set()

            # if just the first target of the memo is the target eg: L then cycle break, this is bad

            corner_buffers = cube.corner_memo_buffers
            for pair in corner_memo:
                if len(pair) == 4 or len(pair) == 2:
                    pair_len_half = len(pair) // 2
                    a = pair[:pair_len_half]
                    b = pair[pair_len_half:]
                    # print(pair, pair_len_half, a, b)
                else:
                    a = pair
                    b = ''
                if a in corner_buffers or b in corner_buffers:
                    break
                no_cycle_break_corner_memo.add(pair)

            alg_to_drill = algs_to_drill.intersection(no_cycle_break_corner_memo)

            # if all are same value inc count by 2
            # determine if max min deviation is more than ±1
            # find max
            # find min
            # find difference

            if algs_to_drill.intersection(no_cycle_break_corner_memo):
                # print(max(alg_freq_dist.values()),  min(alg_freq_dist.values()), max(alg_freq_dist.values())-min(alg_freq_dist.values()))

                alg_to_drill = alg_to_drill.pop()
                # check if freq is < count and if so continue
                if alg_freq_dist[alg_to_drill] < count:
                    alg_freq_dist[alg_to_drill] += 1
                elif len(set(alg_freq_dist.values())) == 1:
                    count += inc_amt
                else:
                    continue

                # print(alg_to_drill)
                # print(alg_freq_dist, sep="")
                # print(corner_memo)
                # print(no_cycle_break_corner_memo)
                print(self.reduce_scramble(scramble))
                input()

            if count > 2:
                return

    def drill_edge_buffer(self, edge_buffer: str):
        # todo add edge flips
        exclude_from_memo = set()
        # todo store all len of all buffers
        num = 1
        while len(exclude_from_memo) < 360:
            print(f'Num: {num}/72', len(exclude_from_memo))
            memo = self.generate_random_edge_memo(edge_buffer, exclude_from_memo)
            for i in memo:
                exclude_from_memo.add(i)
            num += 1
            print(self.memo_edges())
            input()

    def generate_random_edge_memo(self, edge_buffer=None, exclude_from_memo=None):
        # TODO this is for drilling all floating buffers and potentially not repeating a letter pair
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = self.default_edge_buffer if edge_buffer is None else edge_buffer
        memo = []
        edges = self.adj_edges.copy()

        edges = self.remove_irrelevant_edge_buffers(edges, edge_buffer)

        while edges:
            print(edges)

            edge, edge2 = random.sample(list(edges), k=2)

        if len(memo) % 2 == 1:
            memo.pop()

        self.scramble_edges_from_memo(memo, str(edge_buffer))
        return self.format_edge_memo(memo)

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


if __name__ == "__main__":
    s = "F2 D2 R' D2 F2 R2 U2 B2 L2 R B' U' R F' D R U' B' D' L"
    s = "L' R B U2 B' L2 R2 F2 L' R U' F2 U'"
    s = "R U' D'  R' U R  D2 R' U' R D2 D U R'"
    c = Cube("", ls=letter_scheme)
    print(c.adj_corners)
    c.display_cube()
    # todo adapt for different versions of FDR ie FRD
    c.drill_corner_sticker('FDR')
    # c.drill_edge_sticker("UL")
