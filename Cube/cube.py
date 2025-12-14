import json
from collections import deque
from typing import Optional

import kociemba

import dlin
from comms.comms import COMMS
from Commutator.comm_shift import comm_shift
from Cube.letterscheme import LetterScheme
from Settings.settings import Buffers, Settings

from .face_enum import CornerFaceEnum as Corner
from .face_enum import EdgeFaceEnum
from .face_enum import EdgeFaceEnum as Edge

DEBUG = True


class Cube:
    def __init__(
        self,
        s: str = "",
        can_parity_swap: bool = False,
        auto_scramble: bool = True,
        ls: Optional[LetterScheme] = None,
        buffers: Optional[Buffers] = None,
        parity_swap_edges: Optional[str] = None,
        buffer_order: Optional[dict[str, list[str]]] = None,
        settings=None,
    ):

        self.scramble: list[str] = s.rstrip("\n").strip().split()
        self.has_parity: bool = (len(self.scramble) - s.count("2")) % 2 == 1
        self.kociemba_order: str = "URFDLB"
        self.kociemba_solved_cube: str = (
            "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        )
        self.faces: str = "ULFRBD"
        use_default_letter_scheme = True if ls is None else False
        if type(ls) is LetterScheme:
            self.ls: LetterScheme = ls
        else:
            ls: letter_scheme = LetterScheme(ls, use_default=use_default_letter_scheme)
            self.ls: LetterScheme = ls

        self.settings: Settings = settings if settings is not None else Settings()

        self.slices: str = "MSE"

        self.directions: list[str] = ["", "'", "2"]
        self.opp_faces: dict[str, str] = {
            "U": "D",
            "D": "U",
            "F": "B",
            "B": "F",
            "L": "R",
            "R": "L",
        }

        # letter scheme
        UB, UR, UF, UL = ls["UB"], ls["UR"], ls["UF"], ls["UL"]
        LU, LF, LD, LB = ls["LU"], ls["LF"], ls["LD"], ls["LB"]
        FU, FR, FD, FL = ls["FU"], ls["FR"], ls["FD"], ls["FL"]
        RU, RB, RD, RF = ls["RU"], ls["RB"], ls["RD"], ls["RF"]
        BU, BL, BD, BR = ls["BU"], ls["BL"], ls["BD"], ls["BR"]
        DF, DR, DB, DL = ls["DF"], ls["DR"], ls["DB"], ls["DL"]

        UBL, UBR, UFR, UFL = ls["UBL"], ls["UBR"], ls["UFR"], ls["UFL"]
        LUB, LUF, LDF, LDB = ls["LUB"], ls["LUF"], ls["LDF"], ls["LDB"]
        FUL, FUR, FDR, FDL = ls["FUL"], ls["FUR"], ls["FDR"], ls["FDL"]
        RUF, RUB, RDB, RDF = ls["RUF"], ls["RUB"], ls["RDB"], ls["RDF"]
        BUR, BUL, BDL, BDR = ls["BUR"], ls["BUL"], ls["BDL"], ls["BDR"]
        DFL, DFR, DBR, DBL = ls["DFL"], ls["DFR"], ls["DBR"], ls["DBL"]

        if buffers is not None:
            self.default_edge_buffer: str = ls[buffers["edge_buffer"]]
            self.default_corner_buffer: str = ls[buffers["corner_buffer"]]
        else:
            self.default_edge_buffer: str = ls["UF"]
            self.default_corner_buffer: str = ls["UFR"]

        self.edge_memo_buffers: set[str] = set()
        self.corner_memo_buffers: set[str] = set()

        self.corner_cycle_break_order: list[str] = [UBR, UBL, UFL, RDF, RDB, LDF, LDB]
        self.edge_cycle_break_order: list[str] = [
            UB,
            UR,
            UL,
            DF,
            FR,
            FL,
            DR,
            DL,
            BR,
            BL,
        ]

        self.corner_buffer_order = self.settings.buffer_order["corners"]
        self.edge_buffer_order = self.settings.buffer_order["edges"]

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

        self.default_edges = (
            self.U_edges
            + self.L_edges
            + self.F_edges
            + self.R_edges
            + self.B_edges
            + self.D_edges
        )
        self.default_corners = (
            self.U_corners
            + self.L_corners
            + self.F_corners
            + self.R_corners
            + self.B_corners
            + self.D_corners
        )

        self.u_adj_edges_index = [Edge.UP, Edge.UP, Edge.UP, Edge.UP]
        self.l_adj_edges_index = [Edge.LEFT, Edge.LEFT, Edge.LEFT, Edge.RIGHT]
        self.f_adj_edges_index = [Edge.DOWN, Edge.LEFT, Edge.UP, Edge.RIGHT]
        self.r_adj_edges_index = [Edge.RIGHT, Edge.LEFT, Edge.RIGHT, Edge.RIGHT]
        self.b_adj_edges_index = [Edge.UP, Edge.LEFT, Edge.DOWN, Edge.RIGHT]
        self.d_adj_edges_index = [Edge.DOWN, Edge.DOWN, Edge.DOWN, Edge.DOWN]

        self.u_adj_edges = [self.B_edges, self.R_edges, self.F_edges, self.L_edges]
        self.r_adj_edges = [self.U_edges, self.B_edges, self.D_edges, self.F_edges]
        self.l_adj_edges = [self.U_edges, self.F_edges, self.D_edges, self.B_edges]
        self.f_adj_edges = [self.U_edges, self.R_edges, self.D_edges, self.L_edges]
        self.b_adj_edges = [self.U_edges, self.L_edges, self.D_edges, self.R_edges]
        self.d_adj_edges = [self.F_edges, self.R_edges, self.B_edges, self.L_edges]

        all_edges = [
            self.U_edges,
            self.L_edges,
            self.F_edges,
            self.R_edges,
            self.B_edges,
            self.D_edges,
        ]
        all_adj_edges = [
            self.u_adj_edges,
            self.l_adj_edges,
            self.f_adj_edges,
            self.r_adj_edges,
            self.b_adj_edges,
            self.d_adj_edges,
        ]
        all_adj_edges_index = [
            self.u_adj_edges_index,
            self.l_adj_edges_index,
            self.f_adj_edges_index,
            self.r_adj_edges_index,
            self.b_adj_edges_index,
            self.d_adj_edges_index,
        ]

        self.adj_edges = {}
        for face, adjacents, adj_indexes in zip(
            all_edges, all_adj_edges, all_adj_edges_index
        ):
            for face_pos, adj, adj_index in zip(Edge, adjacents, adj_indexes):
                self.adj_edges[face[face_pos]] = adj[adj_index]

        self.adj_corners = {
            self.U_corners[Corner.UPLEFT]: [
                self.B_corners[Corner.UPRIGHT],
                self.L_corners[Corner.UPLEFT],
            ],
            self.U_corners[Corner.UPRIGHT]: [
                self.R_corners[Corner.UPRIGHT],
                self.B_corners[Corner.UPLEFT],
            ],
            self.U_corners[Corner.DOWNRIGHT]: [
                self.F_corners[Corner.UPRIGHT],
                self.R_corners[Corner.UPLEFT],
            ],
            self.U_corners[Corner.DOWNLEFT]: [
                self.L_corners[Corner.UPRIGHT],
                self.F_corners[Corner.UPLEFT],
            ],
            self.L_corners[Corner.UPLEFT]: [
                self.U_corners[Corner.UPLEFT],
                self.B_corners[Corner.UPRIGHT],
            ],
            self.L_corners[Corner.UPRIGHT]: [
                self.F_corners[Corner.UPLEFT],
                self.U_corners[Corner.DOWNLEFT],
            ],
            self.L_corners[Corner.DOWNRIGHT]: [
                self.D_corners[Corner.UPLEFT],
                self.F_corners[Corner.DOWNLEFT],
            ],
            self.L_corners[Corner.DOWNLEFT]: [
                self.B_corners[Corner.DOWNRIGHT],
                self.D_corners[Corner.DOWNLEFT],
            ],
            self.F_corners[Corner.UPLEFT]: [
                self.U_corners[Corner.DOWNLEFT],
                self.L_corners[Corner.UPRIGHT],
            ],
            self.F_corners[Corner.UPRIGHT]: [
                self.R_corners[Corner.UPLEFT],
                self.U_corners[Corner.DOWNRIGHT],
            ],
            self.F_corners[Corner.DOWNRIGHT]: [
                self.D_corners[Corner.UPRIGHT],
                self.R_corners[Corner.DOWNLEFT],
            ],
            self.F_corners[Corner.DOWNLEFT]: [
                self.L_corners[Corner.DOWNRIGHT],
                self.D_corners[Corner.UPLEFT],
            ],
            self.R_corners[Corner.UPLEFT]: [
                self.U_corners[Corner.DOWNRIGHT],
                self.F_corners[Corner.UPRIGHT],
            ],
            self.R_corners[Corner.UPRIGHT]: [
                self.B_corners[Corner.UPLEFT],
                self.U_corners[Corner.UPRIGHT],
            ],
            self.R_corners[Corner.DOWNRIGHT]: [
                self.D_corners[Corner.DOWNRIGHT],
                self.B_corners[Corner.DOWNLEFT],
            ],
            self.R_corners[Corner.DOWNLEFT]: [
                self.F_corners[Corner.DOWNRIGHT],
                self.D_corners[Corner.UPRIGHT],
            ],
            self.B_corners[Corner.UPLEFT]: [
                self.U_corners[Corner.UPRIGHT],
                self.R_corners[Corner.UPRIGHT],
            ],
            self.B_corners[Corner.UPRIGHT]: [
                self.L_corners[Corner.UPLEFT],
                self.U_corners[Corner.UPLEFT],
            ],
            self.B_corners[Corner.DOWNRIGHT]: [
                self.D_corners[Corner.DOWNLEFT],
                self.L_corners[Corner.DOWNLEFT],
            ],
            self.B_corners[Corner.DOWNLEFT]: [
                self.R_corners[Corner.DOWNRIGHT],
                self.D_corners[Corner.DOWNRIGHT],
            ],
            self.D_corners[Corner.UPLEFT]: [
                self.F_corners[Corner.DOWNLEFT],
                self.L_corners[Corner.DOWNRIGHT],
            ],
            self.D_corners[Corner.UPRIGHT]: [
                self.R_corners[Corner.DOWNLEFT],
                self.F_corners[Corner.DOWNRIGHT],
            ],
            self.D_corners[Corner.DOWNRIGHT]: [
                self.B_corners[Corner.DOWNLEFT],
                self.R_corners[Corner.DOWNRIGHT],
            ],
            self.D_corners[Corner.DOWNLEFT]: [
                self.L_corners[Corner.DOWNLEFT],
                self.B_corners[Corner.DOWNRIGHT],
            ],
        }

        self.u_adj_corners = [
            self.B_corners,
            self.R_corners,
            self.F_corners,
            self.L_corners,
        ]
        self.r_adj_corners = [
            self.U_corners,
            self.B_corners,
            self.D_corners,
            self.F_corners,
        ]
        self.l_adj_corners = [
            self.U_corners,
            self.F_corners,
            self.D_corners,
            self.B_corners,
        ]
        self.f_adj_corners = [
            self.U_corners,
            self.R_corners,
            self.D_corners,
            self.L_corners,
        ]
        self.b_adj_corners = [
            self.U_corners,
            self.L_corners,
            self.D_corners,
            self.R_corners,
        ]
        self.d_adj_corners = [
            self.F_corners,
            self.R_corners,
            self.B_corners,
            self.L_corners,
        ]

        self.u_adj_corners_index = [
            (Corner.UPRIGHT, Corner.UPLEFT),
            (Corner.UPRIGHT, Corner.UPLEFT),
            (Corner.UPRIGHT, Corner.UPLEFT),
            (Corner.UPRIGHT, Corner.UPLEFT),
        ]
        self.r_adj_corners_index = [
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
        ]
        self.l_adj_corners_index = [
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
        ]
        self.f_adj_corners_index = [
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.UPRIGHT, Corner.UPLEFT),
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
        ]
        self.b_adj_corners_index = [
            (Corner.UPRIGHT, Corner.UPLEFT),
            (Corner.UPLEFT, Corner.DOWNLEFT),
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
            (Corner.DOWNRIGHT, Corner.UPRIGHT),
        ]
        self.d_adj_corners_index = [
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
            (Corner.DOWNLEFT, Corner.DOWNRIGHT),
        ]

        # Starting from UF following L
        self.m_edges_index = [Edge.DOWN, Edge.DOWN, Edge.DOWN, Edge.UP]
        self.m_adj_edges_index = [Edge.UP, Edge.UP, Edge.DOWN, Edge.UP]
        # Starting from UR following F
        self.s_edges_index = [Edge.RIGHT, Edge.DOWN, Edge.LEFT, Edge.UP]
        self.s_adj_edges_index = [Edge.UP, Edge.RIGHT, Edge.DOWN, Edge.LEFT]
        # Starting from FR following D
        self.e_edges_index = [Edge.RIGHT, Edge.RIGHT, Edge.RIGHT, Edge.RIGHT]
        self.e_adj_edges_index = [Edge.LEFT, Edge.LEFT, Edge.LEFT, Edge.LEFT]

        self.wide_moves = {
            "u": ("E", -1),
            "r": ("M", -1),
            "f": ("S", 1),
            "l": ("M", 1),
            "d": ("E", 1),
            "b": ("S", -1),
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

        self.moves_map = {
            "U": (
                self.U_edges,
                self.u_adj_edges,
                self.u_adj_edges_index,
                self.U_corners,
                self.u_adj_corners,
                self.u_adj_corners_index,
            ),
            "R": (
                self.R_edges,
                self.r_adj_edges,
                self.r_adj_edges_index,
                self.R_corners,
                self.r_adj_corners,
                self.r_adj_corners_index,
            ),
            "L": (
                self.L_edges,
                self.l_adj_edges,
                self.l_adj_edges_index,
                self.L_corners,
                self.l_adj_corners,
                self.l_adj_corners_index,
            ),
            "F": (
                self.F_edges,
                self.f_adj_edges,
                self.f_adj_edges_index,
                self.F_corners,
                self.f_adj_corners,
                self.f_adj_corners_index,
            ),
            "B": (
                self.B_edges,
                self.b_adj_edges,
                self.b_adj_edges_index,
                self.B_corners,
                self.b_adj_corners,
                self.b_adj_corners_index,
            ),
            "D": (
                self.D_edges,
                self.d_adj_edges,
                self.d_adj_edges_index,
                self.D_corners,
                self.d_adj_corners,
                self.d_adj_corners_index,
            ),
            "M": (
                [self.U_edges, self.F_edges, self.D_edges, self.B_edges],
                [self.F_edges, self.D_edges, self.B_edges, self.U_edges],
                self.m_edges_index,
                self.m_adj_edges_index,
            ),
            "S": (
                [self.U_edges, self.R_edges, self.D_edges, self.L_edges],
                [self.R_edges, self.D_edges, self.L_edges, self.U_edges],
                self.s_edges_index,
                self.s_adj_edges_index,
            ),
            "E": (
                [self.F_edges, self.R_edges, self.B_edges, self.L_edges],
                [self.R_edges, self.B_edges, self.L_edges, self.F_edges],
                self.e_edges_index,
                self.e_adj_edges_index,
            ),
        }

        self.parity_swap_edges = (
            parity_swap_edges.upper() if parity_swap_edges is not None else "UF-UR"
        )
        # UF-UR swap
        if can_parity_swap:
            self.parity_swap()

        if auto_scramble:
            self.scramble_cube()

    def get_piece_map(self, piece) -> tuple[deque[str], EdgeFaceEnum]:
        return {
            "UB": (self.U_edges, Edge.UP),
            "UR": (self.U_edges, Edge.RIGHT),
            "UF": (self.U_edges, Edge.DOWN),
            "UL": (self.U_edges, Edge.LEFT),
            "LU": (self.L_edges, Edge.UP),
            "LF": (self.L_edges, Edge.RIGHT),
            "LD": (self.L_edges, Edge.DOWN),
            "LB": (self.L_edges, Edge.LEFT),
            "FU": (self.F_edges, Edge.UP),
            "FR": (self.F_edges, Edge.RIGHT),
            "FD": (self.F_edges, Edge.DOWN),
            "FL": (self.F_edges, Edge.LEFT),
            "RU": (self.R_edges, Edge.UP),
            "RB": (self.R_edges, Edge.RIGHT),
            "RD": (self.R_edges, Edge.DOWN),
            "RF": (self.R_edges, Edge.LEFT),
            "BU": (self.B_edges, Edge.UP),
            "BR": (self.B_edges, Edge.RIGHT),
            "BD": (self.B_edges, Edge.DOWN),
            "BL": (self.B_edges, Edge.LEFT),
            "DF": (self.D_edges, Edge.UP),
            "DR": (self.D_edges, Edge.RIGHT),
            "DB": (self.D_edges, Edge.DOWN),
            "DL": (self.D_edges, Edge.LEFT),
        }[piece]

    # memo

    def parity_swap(self):
        # FIXME: this should support more than just UF-UR and UL-UB
        if not self.has_parity:
            return

        swap = (
            self.parity_swap_edges
            if self.parity_swap_edges is not None
            else self.settings.parity_swap_edges
        )

        piece_a, piece_b = swap.split("-")
        a, b = self.get_piece_map(piece_a), self.get_piece_map(piece_b)
        if a is None or b is None:
            raise ValueError(
                "Parity swap is an invalid value: {self.parity_swap_edges}"
            )

        piece_a_adj, piece_b_adj = piece_a[::-1], piece_b[::-1]
        a_adj, b_adj = self.get_piece_map(piece_a_adj), self.get_piece_map(piece_b_adj)
        if a_adj is None or b_adj is None:
            raise ValueError(
                "Parity swap is an invalid value: {self.parity_swap_edges}"
            )

        a_face, b_face = piece_a[0], piece_b[0]
        a_face_adj, b_face_adj = piece_a_adj[0], piece_b_adj[0]

        a_faces, a_dir = a
        b_faces, b_dir = b

        a_faces_adj, a_dir_adj = a_adj
        b_faces_adj, b_dir_adj = b_adj

        new_a = a_faces.copy()
        new_a[a_dir] = b_faces[b_dir]
        setattr(self, f"{a_face}_edges", new_a)

        b_faces, b_dir = self.get_piece_map(piece_b)

        new_b = b_faces.copy()
        new_b[b_dir] = a_faces[a_dir]
        setattr(self, f"{b_face}_edges", new_b)

        new_a_adj = a_faces_adj.copy()
        new_a_adj[a_dir_adj] = b_faces_adj[b_dir_adj]
        setattr(self, f"{a_face_adj}_edges", new_a_adj)

        b_faces_adj, b_dir_adj = self.get_piece_map(piece_b_adj)

        new_b_adj = b_faces_adj.copy()
        new_b_adj[b_dir_adj] = a_faces_adj[a_dir_adj]
        setattr(self, f"{b_face_adj}_edges", new_b_adj)

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        for (edges, corners), (edges2, corners2) in zip(
            self.cube_faces().values(), other.cube_faces().values()
        ):
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

    def do_move(self, move: str, invert_direction: bool = False):
        if not move:
            return

        elif len(move) > 3:
            raise ValueError("Invalid move length", move)

        has_wide_move = False
        if "w" in move:
            move = move.replace("w", "")
            has_wide_move = True

        rotation = self.rotations_map[move[1:]]

        face_turn = move[:1]

        if face_turn in ("x", "y", "z"):
            self.do_cube_rotation(face_turn)

        elif has_wide_move and face_turn in self.faces:
            self._rotate_wide(move.lower())
        elif face_turn in self.faces:
            side = self.moves_map.get(face_turn)
            self._rotate_layer(rotation, *side, invert_direction=invert_direction)
        elif face_turn in self.slices:
            side = self.moves_map.get(face_turn)
            self._rotate_slice(rotation, *side, invert_direction=invert_direction)
        elif face_turn.islower():
            self._rotate_wide(move)

    def do_cube_rotation(self, rotation: str):
        cube_rotation_map = {"x": ("r", "L"), "y": ("u", "D"), "z": ("f", "B")}
        rotation_move = rotation[:1]
        move_dir = rotation[1:]
        a, b = cube_rotation_map[rotation_move]
        self.do_move(a + move_dir)
        self.do_move(b + move_dir, invert_direction=True)

    @staticmethod
    def _rotate_layer(
        rotation,
        edges,
        adj_edges,
        adj_edges_index,
        corners,
        adj_corners,
        adj_corners_index,
        invert_direction=False,
    ):
        if invert_direction:
            rotation *= -1

        edges.rotate(rotation)
        corners.rotate(rotation)

        # rotate adjacent of the side edges
        side = deque([i[j] for i, j in zip(adj_edges, adj_edges_index)])
        side.rotate(rotation)
        for adj_side_obj, adj_edges_index, side_slice in zip(
            adj_edges, adj_edges_index, side
        ):
            adj_side_obj[adj_edges_index] = side_slice

        # rotate adjacent of the side corners
        side = deque(
            [
                (layer[i], layer[j])
                for layer, (i, j) in zip(adj_corners, adj_corners_index)
            ]
        )
        side.rotate(rotation)
        for adj_side_obj, (i, j), (a, b) in zip(adj_corners, adj_corners_index, side):
            adj_side_obj[i] = a
            adj_side_obj[j] = b

    @staticmethod
    def _rotate_slice(
        rotation, edges, adj_edges, edges_index, adj_edges_index, invert_direction=False
    ):
        if invert_direction:
            rotation *= -1
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
        return [
            default
            for default, current in zip(self.default_corners, self.all_corners)
            if default == current
            and default != self.default_corner_buffer
            and default not in self.adj_corners[self.default_corner_buffer]
        ]

    @property
    def twisted_corners(self):
        return {
            default: current
            for default, current in zip(self.default_corners, self.all_corners)
            if default in self.adj_corners[current]
            and default != self.default_corner_buffer
            and default not in self.adj_corners[self.default_corner_buffer]
        }

    @property
    def twisted_corners_count(self):
        return len(self.twisted_corners) // 3

    @property
    def solved_edges(self):
        return [
            default
            for default, current in zip(self.default_edges, self.all_edges)
            if default == current
            and default != self.default_edge_buffer
            and default != self.adj_edges[self.default_edge_buffer]
        ]

    @property
    def flipped_edges(self):
        return {
            default: current
            for default, current in zip(self.default_edges, self.all_edges)
            if default == self.adj_edges[current]
            and default != self.default_edge_buffer
            and default != self.adj_edges[self.default_edge_buffer]
        }

    @property
    def all_edges(self):
        return (
            self.U_edges
            + self.L_edges
            + self.F_edges
            + self.R_edges
            + self.B_edges
            + self.D_edges
        )

    @property
    def all_corners(self):
        return (
            self.U_corners
            + self.L_corners
            + self.F_corners
            + self.R_corners
            + self.B_corners
            + self.D_corners
        )

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
        all_edges = [
            self.U_edges,
            self.L_edges,
            self.F_edges,
            self.R_edges,
            self.B_edges,
            self.D_edges,
        ]
        all_corners = [
            self.U_corners,
            self.L_corners,
            self.F_corners,
            self.R_corners,
            self.B_corners,
            self.D_corners,
        ]
        return {
            face: pieces for face, *pieces in zip(self.faces, all_edges, all_corners)
        }

    def display_cube(self):
        for name, (e, c) in self.cube_faces().items():
            print("-------", name, "-------")
            print(f"      {c[Corner.UPLEFT]} {e[Edge.UP]} {c[Corner.UPRIGHT]}     ")
            print(f"      {e[Edge.LEFT]}   {e[Edge.RIGHT]}      ")
            print(
                f"      {c[Corner.DOWNLEFT]} {e[Edge.DOWN]} {c[Corner.DOWNRIGHT]}   \n"
            )

    def scramble_cube(self, scramble=None):
        # self.display_cube()
        if scramble is None:
            scramble = self.scramble
        else:
            scramble = scramble.rstrip("\n").strip().split()

        for move in scramble:
            self.do_move(move)

        trace = self.get_dlin_trace()

        # # self.display_cube()
        rotations = trace["rotation"]
        for rotation in rotations:
            self.do_cube_rotation(rotation)
        #
        # self.display_cube()

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

    def scramble_corners_from_memo(self, memo, corner_buffer: Optional[str] = None):
        corner_buffer = (
            self.default_corner_buffer if corner_buffer is None else corner_buffer
        )
        iter_memo = iter(memo)
        self._reset()
        for target in iter_memo:
            a = str(target)
            b = str(next(iter_memo))

            comm = comm_shift(COMMS, corner_buffer, a, b)
            self.scramble_cube(comm)

        return self.solve()

    def _reset(self):
        self.__init__()

    def get_faces_colors(self):
        cube_faces = self.cube_faces()
        cube_string = ""
        for face_name in self.kociemba_order:
            e, c = cube_faces.get(face_name)
            face = c[Corner.UPLEFT][0] + e[Edge.UP][0] + c[Corner.UPRIGHT][0]
            face += e[Edge.LEFT][0] + face_name + e[Edge.RIGHT][0]
            face += c[Corner.DOWNLEFT][0] + e[Edge.DOWN][0] + c[Corner.DOWNRIGHT][0]
            cube_string += face
        return cube_string

    def get_dlin_trace(self):
        if self.has_parity:
            swap = self.parity_swap_edges.split("-")
        else:
            swap = None
        scram = (
            " ".join(self.scramble) if type(self.scramble) is list else self.scramble
        )
        return dlin.trace(scramble=scram, swap=swap, buffers=self.settings.dlin_buffers)

    def solve(self, max_depth=20, invert=False):
        # TODO:::: fix this to accept both letter schemes
        if not self.ls.is_default:
            raise Exception("letter scheme must be default in order to solve cube")
        if not invert:
            return kociemba.solve(self.get_faces_colors(), max_depth=max_depth)
        else:
            return kociemba.solve(
                self.kociemba_solved_cube, self.get_faces_colors(), max_depth=max_depth
            )


if __name__ == "__main__":
    from pathlib import Path

    # Get the directory containing this file
    module_dir = Path(__file__).parent
    # Go up one level to root and find settings.json
    settings_path = module_dir.parent / "settings.json"

    with open(settings_path) as f:
        settings = json.loads(f.read())
        letter_scheme = settings["letter_scheme"]
    #     buffers = settings['buffers']
    # # s = "F2 D2 R' D2 F2 R2 U2 B2 L2 R B' U' R F' D R U' B' D' L"
    # scram = "L' R B U2 B' L2 R2 F2 L' R U' F2 U'"
    # # s = "R U' D'  R' U R  D2 R' U' R D2 D U R'"
    #
    # print(Cube("B R L B' U B2 F2 R F D2 B' R2 U2 D B F D F L' U2 B D' R2").twisted_corners_count)
    # scram = "R U R' U' " * 6
    # scram += "F4 B4 L4 R4 D4 R4 B4 U4 R4 L4 S4 E4 M4 S4 L4 F4 U4"
    scram = "R U R'"
    scram = "D"

    cube = Cube(
        scram, ls=letter_scheme, parity_swap_edges="UF-UR", can_parity_swap=True
    )
    print(scram)
    # # print(c.adj_corners)
    cube.display_cube()
    print(cube.get_faces_colors())
    # print(cube.solve(invert=False))
    # print(cube.solve(invert=True))
    # # # TODO:::: adapt for different versions of FDR ie FRD
    # # # c.drill_corner_sticker('FDR')
    # # # TODO:::: letter scheme for below is a dependency for working
    # # c.drill_edge_buffer("DF")
