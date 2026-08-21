import logging
import Settings.settings
from dlin.tracer import rotate_face_precedence
import random
from collections import deque, defaultdict
from typing import Optional

import dlin
import kociemba
import numpy as np
from comms.comms import COMMS
from Commutator.comm_shift import comm_shift
from interface import CLIInterface, OutputMode
from Letterscheme.letterscheme import LetterScheme
from Settings.settings import Buffers, Settings
from dlin.piece import Piece

from .face_enum import CornerFaceEnum as Corner
from .face_enum import EdgeFaceEnum
from .face_enum import EdgeFaceEnum as Edge


import time

DEBUG = True


# ---------------------------------------------------------------------------
# Shared helpers (edges) -- used by both Cube.generate_scramble_state and,
# indirectly, by nothing corner-related (corners have their own copies below
# where the logic actually differs).
# ---------------------------------------------------------------------------

AXIS_OF_LETTER = {"U": 1, "D": 1, "F": 2, "B": 2, "R": 0, "L": 0}


EDGE_COLORS = {
    0: ("U", "F"),
    1: ("U", "B"),
    2: ("U", "R"),
    3: ("U", "L"),
    4: ("D", "F"),
    5: ("D", "R"),
    6: ("D", "B"),
    7: ("D", "L"),
    8: ("F", "R"),
    9: ("F", "L"),
    10: ("B", "L"),
    11: ("B", "R"),
}


def select_cycles(
    categorize_cycles: dict[tuple[str, str], list[str]],
    max_cycle_len: int = 3,
) -> list[str]:
    keys = list(categorize_cycles.keys())
    random.shuffle(keys)  # randomness lives here

    used = set()
    cycles = []
    for a, b in keys:
        if len(cycles) >= max_cycle_len:
            break
        if a not in used and b not in used:
            cycles.append(random.choice(categorize_cycles[(a, b)]))
            used.add(a)
            used.add(b)

    return cycles


def edge_perm_parity(perm):
    """Generic permutation-array parity check (works for any length --
    also reused as `perm_parity` for corners)."""
    visited = [False] * len(perm)
    swaps = 0
    for i in range(len(perm)):
        if visited[i]:
            continue
        j, clen = i, 0
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            clen += 1
        swaps += clen - 1
    return swaps % 2


# alias used by the corner-generation code (identical implementation)
perm_parity = edge_perm_parity


def edge_perm_parity_sub(perm, positions):
    """Permutation parity over just the given subset (for when some
    positions -- e.g. a pseudo-swapped pair -- are handled separately)."""
    positions = list(positions)
    index_of = {p: i for i, p in enumerate(positions)}
    sub = [index_of[perm[p]] for p in positions]
    visited = [False] * len(sub)
    swaps = 0
    for i in range(len(sub)):
        if visited[i]:
            continue
        j, clen = i, 0
        while not visited[j]:
            visited[j] = True
            j = sub[j]
            clen += 1
        swaps += clen - 1
    return swaps % 2


def chain_into_permutation(permutation_state, start_pos, links):
    """
    Threads (a, b) blocks into one closed permutation cycle starting AND
    ending at start_pos. `start_pos` must never itself appear inside `links`
    -- it's purely the silent entry/anchor point, never an explicit hop.
    Every block always contributes exactly 2 hops, so any (pos_a, pos_b)
    target block stays paired together as a written trace pair no matter
    where it falls in the shuffle or how many other blocks share the cycle.
    """
    cur = start_pos
    for a, b in links:
        permutation_state[cur] = a
        cur = a
        if b is not None:
            permutation_state[cur] = b
            cur = b
    permutation_state[cur] = start_pos


def build_natural_filler_cycles(positions, avg_cycle_len=3.0):
    """Splits leftover positions into a natural mix of cycle lengths --
    including length-1 (fixed points), which are the in-place-flip candidates."""
    positions = list(positions)
    random.shuffle(positions)
    cycles = []
    i, n = 0, len(positions)
    while i < n:
        remaining = n - i
        length = 1
        while length < remaining and random.random() < (1 - 1 / avg_cycle_len):
            length += 1
        cycles.append(positions[i : i + length])
        i += length
    return cycles


def build_uniform_random_cycles(positions):
    """
    A genuinely unbiased natural cycle structure: sample a uniformly random
    permutation of `positions` (plain shuffle) and decompose it into its own
    cycles, rather than pre-deciding cycle lengths with an artificial
    distribution. A uniform random permutation has an expected value of
    exactly 1 fixed point, regardless of pool size (basic probability fact)
    -- that's what a real scramble's leftover pieces look like.
    """
    positions = list(positions)
    shuffled = list(positions)
    random.shuffle(shuffled)
    perm_map = dict(zip(positions, shuffled))
    visited = set()
    cycles = []
    for p in positions:
        if p in visited:
            continue
        cyc = []
        cur = p
        while cur not in visited:
            visited.add(cur)
            cyc.append(cur)
            cur = perm_map[cur]
        cycles.append(cyc)
    return cycles


def solve_chain_orientation(
    chain_positions, start_axis, requirements, ori_out, edge_colors
):
    """
    chain_positions: [P_0(buffer, implicit), P_1, ..., P_k] in the EXACT
    order the real Tracer will walk (matches perm[] chain order).
    requirements: dict position -> desired bit (0 = that position's own
    primary letter should be read first, 1 = secondary first) for any
    position that's a locked target.

    The critical fact this encodes, from stepping through Tracer.where_to():
    the letter shown when "visiting" P_i actually spells out P_{i+1}'s own
    identity (since perm[P_i] = P_{i+1}), and its reading direction is
    controlled by ori[P_i] combined with whether the INCOMING axis (itself
    a function of the whole chain walked so far) matches P_i's own primary
    axis type -- not F/B-then-U/D priority, and not P_{i+1}'s own bit.
    So ori_out[P_i] is solved to satisfy P_{i+1}'s requirement.
    """
    current_axis = start_axis
    for i in range(len(chain_positions) - 1):
        P_i = chain_positions[i]
        P_next = chain_positions[i + 1]
        p_primary, _ = edge_colors[P_i]
        axis_matches = current_axis == AXIS_OF_LETTER[p_primary]

        next_primary, next_secondary = edge_colors[P_next]

        if P_next in requirements:
            want_primary_shown = requirements[P_next] == 0
            ori_bit = (
                (0 if want_primary_shown else 1)
                if axis_matches
                else (1 if want_primary_shown else 0)
            )
        else:
            ori_bit = random.randint(0, 1)

        ori_out[P_i] = ori_bit
        primary_shown = (axis_matches and ori_bit == 0) or (
            not axis_matches and ori_bit == 1
        )
        shown_letter = next_primary if primary_shown else next_secondary
        current_axis = AXIS_OF_LETTER[shown_letter]

    ori_out[chain_positions[-1]] = random.randint(
        0, 1
    )  # closes to buffer, unconstrained
    return ori_out


# ---------------------------------------------------------------------------
# Corner-generation helpers (module-level -- these operate independently of
# a Cube instance, mirroring how edge generation is a Cube method but
# corner generation stays a standalone set of functions you can call with
# just a target set).
# ---------------------------------------------------------------------------

CLASS1 = [{"U", "F", "R"}, {"U", "B", "L"}, {"D", "B", "R"}, {"D", "F", "L"}]

CORNER_COLORS = {
    0: "UFR",
    1: "UFL",
    2: "UBL",
    3: "UBR",
    4: "DFR",
    5: "DFL",
    6: "DBR",
    7: "DBL",
}
CORNER_ORI = {
    "BDL": ["LDB", "DBL", "BDL"],
    "BDR": ["RDB", "BDR", "DBR"],
    "BLU": ["LUB", "BUL", "UBL"],
    "BRU": ["RUB", "UBR", "BUR"],
    "DFL": ["LDF", "FDL", "DFL"],
    "DFR": ["RDF", "DFR", "FDR"],
    "FLU": ["LUF", "UFL", "FUL"],
    "FRU": ["RUF", "FUR", "UFR"],
}


def corner_key(s):
    return "".join(sorted(s))


def is_class1(name3):
    return set(name3) in CLASS1


AXIS_SEQUENCE = [1, 2, 0]


def letters_by_axis(name3, reversed_=False):
    out = {}
    for ch in name3:
        out[AXIS_OF_LETTER[ch]] = ch
    if reversed_:
        out[0], out[2] = out[2], out[0]
    return out


def build_corner_sides(cubie_name, position_name, orientation):
    """
    orientation is an internal 0/1/2 slot index (one of the 3 valid physical
    states for this cubie AT THIS POSITION). Corners alternate handedness
    class across the 8 positions (same {UFR,UBL,DBR,DFL} vs {UFL,UBR,DFR,DBL}
    split your Tracer's find_twists()/corner_cycle_ori special-case on) --
    when the cubie's home class differs from the position's class, the R/L
    and F/B axis roles swap relative to the same-class case. Validated
    against 16,000 real scrambled states (dlin.cube.Cube with actual move
    application): 0 mismatches.
    """
    same_class = is_class1(cubie_name) == is_class1(position_name)
    cubie_letters = letters_by_axis(cubie_name, reversed_=not same_class)
    sides = ["", "", ""]
    for i in range(3):
        axis = AXIS_SEQUENCE[i]
        source_axis = AXIS_SEQUENCE[(i - orientation) % 3]
        sides[axis] = cubie_letters[source_axis]
    return sides


def corner_reading(cubie_name, position_name, orientation, axis):
    sides = build_corner_sides(cubie_name, position_name, orientation)
    p = Piece(1, 1, 1)
    p.sides = np.array(sides)
    return p.get_name(axis=axis)


def kociemba_orientation(position_name, my_slot):
    """
    Convert my internal orientation slot into kociemba's own orientation
    number (needed for the sum-of-orientations validity constraint, since
    my slot numbering and kociemba's differ by a fixed, position-only
    permutation -- an artifact of my CORNER_FACELETS table ordering two
    facelets differently than kociemba's own table for exactly the class1
    positions). Harmless for facelet placement itself; only matters for
    this sum check. Self-inverse, so the same function converts either way.
    """
    if is_class1(position_name):
        return [0, 2, 1][my_slot]
    return my_slot


loc_to_perm_corner = {}
for _pos, _name in CORNER_COLORS.items():
    for _reading in CORNER_ORI[corner_key(_name)]:
        loc_to_perm_corner[_reading] = _pos

dlin_buffers_corner = ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"]
corner_buffer_weight = {name: i for i, name in enumerate(dlin_buffers_corner)}


def solve_corner_chain_orientation(chain_positions, start_axis, requirements, ori_out):
    """
    chain_positions: [P_0(buffer, implicit), P_1, ..., P_k] in exact perm[]
    chain order. requirements: dict position -> desired READING STRING
    (e.g. "UFL") for any locked target position.

    Brute-force at each step: try each of the 3 physical orientation slots
    for the occupying cubie, read it via the real Piece.get_name(axis=...),
    and pick whichever slot produces EXACTLY the desired string -- avoids
    needing a numeric orientation formula to be axis-invariant (it isn't).
    """
    current_axis = start_axis
    for i in range(len(chain_positions) - 1):
        P_i = chain_positions[i]
        P_next = chain_positions[i + 1]
        cubie_name = CORNER_COLORS[P_next]
        position_name = CORNER_COLORS[P_i]

        desired = requirements.get(P_next)
        chosen_ori = None
        chosen_reading = None
        candidates = list(range(3))
        random.shuffle(candidates)
        for cand in candidates:
            reading = corner_reading(cubie_name, position_name, cand, current_axis)
            if desired is None or reading == desired:
                chosen_ori, chosen_reading = cand, reading
                break
        if chosen_ori is None:
            raise ValueError(
                f"Could not satisfy corner requirement {desired!r} for position "
                f"{P_next} coming from position {P_i} (axis={current_axis})."
            )
        ori_out[P_i] = chosen_ori
        current_axis = AXIS_OF_LETTER[chosen_reading[0]]

    ori_out[chain_positions[-1]] = random.randint(0, 2)
    return ori_out


def generate_corner_scramble_state(targets, min_pairs=3, force_parity=None, seed=None):
    """
    targets: set of 6-char strings, each a pair of 3-letter corner readings
    concatenated, e.g. "UFLDFR".
    min_pairs: capped at 3 (buffer + 3 pairs = all 7 non-buffer corners).
    force_parity: None / 0 (even) / 1 (odd) permutation parity -- the 50/50
    corner-parity coin flip.

    With only 8 corners, 3 full target pairs use 6 of 7 non-buffer
    positions, leaving exactly 1 free -- forcing a single 7-cycle + 1 fixed
    point (always even parity), no room for a parity fix. When force_parity
    hits this, retry with one fewer target pair to free up room.
    """
    cap = min(min_pairs, 3)
    last_error = None
    for attempt_cap in range(cap, -1, -1):
        try:
            return _generate_corner_scramble_state_once(
                targets, min_pairs=attempt_cap, force_parity=force_parity, seed=seed
            )
        except ValueError as e:
            last_error = e
            continue
    raise last_error


def _generate_corner_scramble_state_once(targets, min_pairs, force_parity, seed):
    if seed is not None:
        random.seed(seed)
    min_pairs = min(min_pairs, 3)

    categorize_cycles = defaultdict(list)
    for pair in targets:
        a, b = pair[:3], pair[3:]
        pos_a, pos_b = loc_to_perm_corner[a], loc_to_perm_corner[b]
        if pos_a == 0 or pos_b == 0:
            continue
        x, y = sorted([pos_a, pos_b])
        categorize_cycles[(x, y)].append((a, b))

    cycles = select_cycles(categorize_cycles, min_pairs)

    target_links = []
    requirements = {}
    used_positions = set()

    for a, b in cycles:
        pos_a, pos_b = loc_to_perm_corner[a], loc_to_perm_corner[b]
        for pos, req in ((pos_a, a), (pos_b, b)):
            if pos in requirements and requirements[pos] != req:
                raise ValueError(
                    f"Conflicting requirement for corner {pos}: {requirements[pos]} vs {req}"
                )
            requirements[pos] = req
        used_positions.add(pos_a)
        used_positions.add(pos_b)
        target_links.append((pos_a, pos_b))

    free_positions = list(set(range(8)) - used_positions - {0})
    random.shuffle(free_positions)
    leftover_pool = list(free_positions)

    permutation_state = list(range(8))
    links = list(target_links)
    reserve = 2 if force_parity is not None else 0
    max_main_filler_pairs = min(3, max(0, len(free_positions) - reserve) // 2)
    num_filler_pairs_main = (
        random.randint(0, max_main_filler_pairs) if max_main_filler_pairs >= 1 else 0
    )
    for _ in range(num_filler_pairs_main):
        if len(free_positions) < 2:
            break
        x, y = free_positions.pop(), free_positions.pop()
        links.append((x, y))
        leftover_pool.remove(x)
        leftover_pool.remove(y)
    random.shuffle(links)

    main_cycle_exists = bool(links)
    if main_cycle_exists:
        chain_into_permutation(permutation_state, 0, links)
    else:
        free_positions.append(0)
        leftover_pool.append(0)

    if free_positions:
        for fc in build_uniform_random_cycles(free_positions):
            if len(fc) == 1:
                permutation_state[fc[0]] = fc[0]
                continue
            f_links = [(fc[i], fc[i + 1]) for i in range(0, len(fc) - 1, 2)]
            if len(fc) % 2 == 1:
                f_links.append((fc[-1], None))
            chain_into_permutation(permutation_state, fc[0], f_links)

    if force_parity is not None and perm_parity(permutation_state) != force_parity:
        fixed_in_leftover = [p for p in leftover_pool if permutation_state[p] == p]
        if len(fixed_in_leftover) >= 2:
            pi, pj = fixed_in_leftover[0], fixed_in_leftover[1]
        elif len(leftover_pool) >= 2:
            pi, pj = leftover_pool[0], leftover_pool[1]
        else:
            raise ValueError(
                "no room to fix corner permutation parity without disturbing a target cycle"
            )
        permutation_state[pi], permutation_state[pj] = (
            permutation_state[pj],
            permutation_state[pi],
        )

    assert sorted(permutation_state) == list(range(8))
    if force_parity is not None:
        assert perm_parity(permutation_state) == force_parity

    orientation = [None] * 8
    if main_cycle_exists:
        chain_positions = [0]
        cur = permutation_state[0]
        while cur != 0:
            chain_positions.append(cur)
            cur = permutation_state[cur]
        ori_map = {}
        solve_corner_chain_orientation(
            chain_positions, start_axis=1, requirements=requirements, ori_out=ori_map
        )
        for pos, bit in ori_map.items():
            orientation[pos] = bit

    remaining = [p for p in range(8) if orientation[p] is None]
    for pos in remaining:
        orientation[pos] = random.randint(0, 2)

    # Validity constraint (sum of orientations == 0 mod 3) is defined in
    # kociemba's numbering, not mine -- convert before checking/fixing.
    total_koc = (
        sum(kociemba_orientation(CORNER_COLORS[p], orientation[p]) for p in range(8))
        % 3
    )
    if total_koc != 0:
        if remaining:
            pos = random.choice(remaining)
            cur_koc = kociemba_orientation(CORNER_COLORS[pos], orientation[pos])
            new_koc = (cur_koc - total_koc) % 3
            orientation[pos] = kociemba_orientation(CORNER_COLORS[pos], new_koc)
        else:
            raise ValueError(
                "no filler corner available to correct orientation sum mod 3"
            )

    return permutation_state, orientation, cycles, requirements, target_links


class Cube:
    def __init__(
        self,
        s: str = "",
        can_parity_swap: bool = False,
        auto_scramble: bool = True,
        ls: LetterScheme | None = None,
        ui: CLIInterface | None = None,
        buffers: Buffers | None = None,
        parity_swap_edges: str | None = None,
        buffer_order: Optional[dict[str, list[str]]] = None,
        settings=None,
    ):
        s = s.replace("3'", "")
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
        elif ls is None:
            ls: letter_scheme = LetterScheme(ls, use_default=use_default_letter_scheme)
            self.ls: LetterScheme = ls
        else:
            raise TypeError(
                f"Cube: letterscheme (type: {type(ls)}) is not of type LetterScheme and is not None"
            )

        self.settings: Settings = settings if settings is not None else Settings(ui)

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

        self.wide_moves: dict[str, tuple[str, int]] = {
            "u": ("E", -1),
            "r": ("M", -1),
            "f": ("S", 1),
            "l": ("M", 1),
            "d": ("E", 1),
            "b": ("S", -1),
        }

        self.notation_to_dir: dict[str, int] = {
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

        self.dir_to_notation: dict[int, str] = {
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
        self.can_parity_swap = can_parity_swap
        # UF-UR swap
        if can_parity_swap:
            self.parity_swap()

        if auto_scramble:
            self.scramble_cube()

    def set_edge_state(self, other: "Cube") -> None:
        if not isinstance(other, Cube):
            raise TypeError(f"Expected a Cube, got {type(other).__name__}")

        self.U_edges = other.U_edges.copy()
        self.L_edges = other.L_edges.copy()
        self.F_edges = other.F_edges.copy()
        self.R_edges = other.R_edges.copy()
        self.B_edges = other.B_edges.copy()
        self.D_edges = other.D_edges.copy()

        # FIX: idk if we need to do this
        if self.can_parity_swap:
            self.parity_swap()

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

    # TODO: fix this for any swap
    def parity_swap(self, parity_swap_edges="UF-UR"):
        if not self.has_parity:
            return

        if parity_swap_edges in {"UF-UR", "UR-UF"} or parity_swap_edges is None:
            self.U_edges[Edge.RIGHT], self.U_edges[Edge.DOWN] = (
                self.U_edges[Edge.DOWN],
                self.U_edges[Edge.RIGHT],
            )
            self.F_edges[Edge.UP], self.R_edges[Edge.UP] = (
                self.R_edges[Edge.UP],
                self.F_edges[Edge.UP],
            )
        elif parity_swap_edges in {"UL-UB", "UB-UL"}:
            self.U_edges[Edge.UP], self.U_edges[Edge.LEFT] = (
                self.U_edges[Edge.LEFT],
                self.U_edges[Edge.UP],
            )
            self.B_edges[Edge.UP], self.L_edges[Edge.UP] = (
                self.L_edges[Edge.UP],
                self.B_edges[Edge.UP],
            )

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented

        if len(self.cube_faces().values()) != len(other.cube_faces().values()):
            return False
        for (edges, corners), (edges2, corners2) in zip(
            self.cube_faces().values(), other.cube_faces().values(), strict=True
        ):
            if edges != edges2 or corners != corners2:
                return False
        return True

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def do_move(self, move: str, invert_direction: bool = False):
        if not move:
            return

        MAX_MOVE_LEN = 3
        if len(move) > MAX_MOVE_LEN:
            raise ValueError("Invalid move length", move)

        has_wide_move = False
        if "w" in move or move.islower():
            move = move.replace("w", "")
            has_wide_move = True

        rotation = self.notation_to_dir[move[1:]]

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
        *,
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
            adj_edges, adj_edges_index, side, strict=True
        ):
            adj_side_obj[adj_edges_index] = side_slice

        # rotate adjacent of the side corners
        side = deque(
            [
                (layer[i], layer[j])
                for layer, (i, j) in zip(adj_corners, adj_corners_index, strict=True)
            ]
        )
        side.rotate(rotation)
        for adj_side_obj, (i, j), (a, b) in zip(adj_corners, adj_corners_index, side):
            adj_side_obj[i] = a
            adj_side_obj[j] = b

    @staticmethod
    def _rotate_slice(
        rotation,
        edges,
        adj_edges,
        edges_index,
        adj_edges_index,
        *,
        invert_direction=False,
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
        rotation = self.notation_to_dir[face_turn[1:]]
        rotation *= direction
        slice_turn = slice_[:1] + self.dir_to_notation[rotation]
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
    def flipped_edges_count(self):
        return len(self.flipped_edges) // 2

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
    def flipped_edges(self) -> dict[str, str]:
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
            return kociemba.solve(
                self.get_faces_colors(),
            )
        else:
            return kociemba.solve(
                self.kociemba_solved_cube,
                self.get_faces_colors(),
            )

    EDGE_COLORS = {
        0: ("U", "F"),
        1: ("U", "B"),
        2: ("U", "R"),
        3: ("U", "L"),
        4: ("D", "F"),
        5: ("D", "R"),
        6: ("D", "B"),
        7: ("D", "L"),
        8: ("F", "R"),
        9: ("F", "L"),
        10: ("B", "L"),
        11: ("B", "R"),
    }

    LOC_TO_PERM_EDGE = {
        "UB": 1,
        "UR": 2,
        "UF": 0,
        "UL": 3,
        "LU": 3,
        "LF": 9,
        "LD": 7,
        "LB": 10,
        "FU": 0,
        "FR": 8,
        "FD": 4,
        "FL": 9,
        "RU": 2,
        "RB": 11,
        "RD": 5,
        "RF": 8,
        "BU": 1,
        "BL": 10,
        "BD": 6,
        "BR": 11,
        "DF": 4,
        "DR": 5,
        "DB": 6,
        "DL": 7,
    }

    @staticmethod
    def letter_orientation(code, loc_to_perm, edge_colors=None):
        """
        Decode orientation (0=oriented, 1=flipped) directly from a
        letter-pair code like 'UB' or 'BU', using the position's
        canonical home reading as reference.
        """
        edge_colors = edge_colors or Cube.EDGE_COLORS
        pos = loc_to_perm[code]
        primary = edge_colors[pos][0]
        return 0 if code[0] == primary else 1

    @staticmethod
    def check_valid_perm(state):
        state = list(state)
        rank = {}
        for i, s in enumerate(sorted(state)):
            rank[s] = i

        state = [rank[s] for s in state]
        res = 0
        c = 0
        while c < len(state):
            if state[c] == c:  # value is home, move on
                c += 1
                continue
            dest = state[c]  # state[c] belongs at index dest
            state[c], state[dest] = state[dest], state[c]  # send it home
            res += 1
        return res % 2 == 0

    @staticmethod
    def edges_to_facelet_string(perm, ori):
        """
        perm[pos] = edge cubie at position pos
        ori[pos] = 0 (oriented) or 1 (flipped)

        Edge numbering:
            0 UF
            1 UB
            2 UR
            3 UL
            4 DF
            5 DR
            6 DB
            7 DL
            8 FR
            9 FL
           10 BL
           11 BR
        """

        facelets = (
            {f"U{i}": "U" for i in range(1, 10)}
            | {f"R{i}": "R" for i in range(1, 10)}
            | {f"F{i}": "F" for i in range(1, 10)}
            | {f"D{i}": "D" for i in range(1, 10)}
            | {f"L{i}": "L" for i in range(1, 10)}
            | {f"B{i}": "B" for i in range(1, 10)}
        )

        edge_facelets = {
            0: ("U8", "F2"),
            1: ("U2", "B2"),
            2: ("U6", "R2"),
            3: ("U4", "L2"),
            4: ("D2", "F8"),
            5: ("D6", "R8"),
            6: ("D8", "B8"),
            7: ("D4", "L8"),
            8: ("F6", "R4"),
            9: ("F4", "L6"),
            10: ("B6", "L4"),
            11: ("B4", "R6"),
        }

        edge_colors = Cube.EDGE_COLORS

        for pos in range(12):
            cubie = perm[pos]
            colors = list(edge_colors[cubie])

            if ori[pos]:
                colors.reverse()

            f1, f2 = edge_facelets[pos]
            facelets[f1] = colors[0]
            facelets[f2] = colors[1]

        order = (
            [f"U{i}" for i in range(1, 10)]
            + [f"R{i}" for i in range(1, 10)]
            + [f"F{i}" for i in range(1, 10)]
            + [f"D{i}" for i in range(1, 10)]
            + [f"L{i}" for i in range(1, 10)]
            + [f"B{i}" for i in range(1, 10)]
        )

        return "".join(facelets[f] for f in order)

    def generate_scramble_state(
        self,
        targets: set[str],
        min_pairs=2,
        fully_excluded: frozenset = frozenset(),
        seed: int | None = None,
    ):
        """
        fully_excluded: positions entirely excluded from this generation --
        never a target, never filler, never the anchor. Empty by default
        (buffer/UF is used as the anchor, just never a target). When the
        corner-parity pseudo-swap is active, pass {0, 2}: the caller sets
        perm[0]/perm[2] directly afterward, and this method's own main cycle
        anchors at whichever position is first in self.settings.dlin_buffers
        edge order among what's left (UB, position 1) -- matching how the
        real Tracer picks its next buffer once 0 and 2 are already
        accounted for.

        Returns (permutation_state, orientation, cycles, requirements,
        target_links).
        """
        if seed is not None:
            random.seed(seed)

        min_pairs = min(min_pairs, 5)

        loc_to_perm = self.LOC_TO_PERM_EDGE

        buffer_weight = {
            buf: i for i, buf in enumerate(self.settings.dlin_buffers["edge"])
        }

        anchor = next(
            loc_to_perm[name]
            for name in self.settings.dlin_buffers["edge"]
            if loc_to_perm[name] not in fully_excluded
        )
        anchor_axis = AXIS_OF_LETTER[self.EDGE_COLORS[anchor][0]]
        target_exclude = set(fully_excluded) | {anchor}

        # ---- 1. Categorize + select targets, excluding buffer/reserved ----
        categorize_cycles: dict[tuple[str, str], list[str]] = defaultdict(list)
        for pair in targets:
            a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
            pos_a, pos_b = loc_to_perm[a], loc_to_perm[b]
            if pos_a in target_exclude or pos_b in target_exclude:
                continue
            ra, rb = rotate_face_precedence(a), rotate_face_precedence(b)
            x, y = sorted([ra, rb], key=lambda k: buffer_weight[k])
            categorize_cycles[(x, y)].append(a + b)

        cycles = select_cycles(categorize_cycles, min_pairs)

        target_links: list[tuple[int, int]] = []
        requirements: dict[int, int] = {}
        used_positions: set[int] = set()

        for pair in cycles:
            a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
            pos_a, pos_b = loc_to_perm[a], loc_to_perm[b]
            req_a = self.letter_orientation(a, loc_to_perm)
            req_b = self.letter_orientation(b, loc_to_perm)
            for pos, req in ((pos_a, req_a), (pos_b, req_b)):
                if pos in requirements and requirements[pos] != req:
                    raise ValueError(
                        f"Conflicting requirement for position {pos}: "
                        f"{requirements[pos]} vs {req} (from pair {pair!r})"
                    )
                requirements[pos] = req
            used_positions.add(pos_a)
            used_positions.add(pos_b)
            target_links.append((pos_a, pos_b))

        # ---- 2. All target blocks thread through ONE cycle anchored at the
        # real buffer (or, when a pseudo-swap reserves it, the next buffer
        # in line). ----
        free_positions = list(
            set(range(12)) - used_positions - set(fully_excluded) - {anchor}
        )
        random.shuffle(free_positions)
        leftover_pool = list(free_positions)

        permutation_state = list(range(12))
        for r in fully_excluded:
            permutation_state[r] = r  # placeholder; caller overwrites these slots
        links = list(target_links)
        max_main_filler_pairs = min(4, max(0, len(free_positions) - 2) // 2)
        num_filler_pairs_main = (
            random.randint(1, max_main_filler_pairs)
            if max_main_filler_pairs >= 1
            else 0
        )
        for _ in range(num_filler_pairs_main):
            if len(free_positions) < 2:
                break
            x, y = free_positions.pop(), free_positions.pop()
            links.append((x, y))
            leftover_pool.remove(x)
            leftover_pool.remove(y)
        random.shuffle(links)

        main_cycle_exists = bool(links)
        if main_cycle_exists:
            chain_into_permutation(permutation_state, anchor, links)
        else:
            free_positions.append(anchor)
            leftover_pool.append(anchor)

        # ---- 3. Remaining positions -> independent natural filler cycles ----
        if free_positions:
            for fc in build_uniform_random_cycles(free_positions):
                if len(fc) == 1:
                    permutation_state[fc[0]] = fc[0]
                    continue
                f_links = [(fc[i], fc[i + 1]) for i in range(0, len(fc) - 1, 2)]
                if len(fc) % 2 == 1:
                    f_links.append((fc[-1], None))
                chain_into_permutation(permutation_state, fc[0], f_links)

        # ---- 4. Fix total permutation parity (over the non-reserved subset) ----
        non_reserved = [p for p in range(12) if p not in fully_excluded]
        if edge_perm_parity_sub(permutation_state, non_reserved) == 1:
            fixed_in_leftover = [p for p in leftover_pool if permutation_state[p] == p]
            if len(fixed_in_leftover) >= 2:
                pi, pj = fixed_in_leftover[0], fixed_in_leftover[1]
            elif len(leftover_pool) >= 2:
                pi, pj = leftover_pool[0], leftover_pool[1]
            else:
                raise ValueError(
                    "No room to fix permutation parity without disturbing a "
                    f"target cycle — used_positions={used_positions}."
                )
            permutation_state[pi], permutation_state[pj] = (
                permutation_state[pj],
                permutation_state[pi],
            )

        assert edge_perm_parity_sub(permutation_state, non_reserved) == 0, (
            "parity fix failed"
        )
        assert sorted(permutation_state[p] for p in non_reserved) == sorted(
            non_reserved
        ), "permutation_state is not a valid bijection"

        # ---- 5. Orientation: solve the MAIN cycle with the chain-aware
        # solver -- this is what actually satisfies the targets. Everything
        # else (pure filler cycles / fixed points, no requirements) gets
        # free random bits. ----
        orientation: list = [None] * 12
        for r in fully_excluded:
            orientation[r] = 0  # placeholder; caller overwrites these slots

        if main_cycle_exists:
            chain_positions = [anchor]
            cur = permutation_state[anchor]
            while cur != anchor:
                chain_positions.append(cur)
                cur = permutation_state[cur]
            ori_map: dict[int, int] = {}
            solve_chain_orientation(
                chain_positions,
                start_axis=anchor_axis,
                requirements=requirements,
                ori_out=ori_map,
                edge_colors=Cube.EDGE_COLORS,
            )
            for pos, bit in ori_map.items():
                orientation[pos] = bit

        remaining = [p for p in range(12) if orientation[p] is None]
        for pos in remaining:
            orientation[pos] = random.randint(0, 1)

        if sum(orientation[p] for p in non_reserved) % 2 == 1:
            if remaining:
                orientation[random.choice(remaining)] ^= 1
            else:
                raise ValueError(
                    "No filler piece available to correct orientation parity."
                )

        return permutation_state, orientation, cycles, requirements, target_links

    # ---- Convenience wrapper: corner generation as a Cube method too, for
    # symmetry with generate_scramble_state (edges). It simply delegates to
    # the module-level corner generator, which has no dependency on a Cube
    # instance's settings. ----
    def generate_corner_scramble_state(
        self, targets, min_pairs=3, force_parity=None, seed=None
    ):
        return generate_corner_scramble_state(
            targets, min_pairs=min_pairs, force_parity=force_parity, seed=seed
        )


# ---------------------------------------------------------------------------
# Full-state (edges + corners) combination: builds a single kociemba facelet
# string directly from the edge/corner permutation+orientation arrays,
# instead of going through a live Cube object's move simulation.
# ---------------------------------------------------------------------------

CORNER_FACELETS = {  # (U/D-facelet, F/B-facelet, R/L-facelet) per position
    0: ("U9", "F3", "R1"),
    1: ("U7", "F1", "L3"),
    2: ("U1", "B3", "L1"),
    3: ("U3", "B1", "R3"),
    4: ("D3", "F9", "R7"),
    5: ("D1", "F7", "L9"),
    6: ("D9", "B7", "R9"),
    7: ("D7", "B9", "L7"),
}

EDGE_FACELETS = {
    0: ("U8", "F2"),
    1: ("U2", "B2"),
    2: ("U6", "R2"),
    3: ("U4", "L2"),
    4: ("D2", "F8"),
    5: ("D6", "R8"),
    6: ("D8", "B8"),
    7: ("D4", "L8"),
    8: ("F6", "R4"),
    9: ("F4", "L6"),
    10: ("B6", "L4"),
    11: ("B4", "R6"),
}


def facelet_order():
    return (
        [f"U{i}" for i in range(1, 10)]
        + [f"R{i}" for i in range(1, 10)]
        + [f"F{i}" for i in range(1, 10)]
        + [f"D{i}" for i in range(1, 10)]
        + [f"L{i}" for i in range(1, 10)]
        + [f"B{i}" for i in range(1, 10)]
    )


def build_facelet_string(edge_perm, edge_ori, corner_perm, corner_ori):
    facelets = {}
    for face in "URFDLB":
        facelets[face + "5"] = face  # centers, always solved

    for pos in range(12):
        cubie = edge_perm[pos]
        colors = list(EDGE_COLORS[cubie])
        if edge_ori[pos]:
            colors.reverse()
        f1, f2 = EDGE_FACELETS[pos]
        facelets[f1] = colors[0]
        facelets[f2] = colors[1]

    for pos in range(8):
        cubie = corner_perm[pos]
        sides = build_corner_sides(
            CORNER_COLORS[cubie], CORNER_COLORS[pos], corner_ori[pos]
        )
        # sides is [X(R/L axis), Y(U/D axis), Z(F/B axis)]
        ud_color, fb_color, rl_color = sides[1], sides[2], sides[0]
        ud_key, fb_key, rl_key = CORNER_FACELETS[pos]
        facelets[ud_key] = ud_color
        facelets[fb_key] = fb_color
        facelets[rl_key] = rl_color

    order = facelet_order()
    return "".join(facelets[f] for f in order)


def generate_cube_state(
    cube, edge_targets, corner_targets, edge_min_pairs=2, corner_min_pairs=3, seed=None
):
    """
    edge_targets and corner_targets are two distinct, independent sets --
    edge_targets holds 4-char strings (two concatenated 2-letter edge
    readings, e.g. "RURD"), corner_targets holds 6-char strings (two
    concatenated 3-letter corner readings, e.g. "UFLDFR"). They're expected
    to be disjoint in content (an edge can't be a corner target and vice
    versa) but nothing stops you from constructing overlapping sets by
    mistake, so this checks lengths explicitly rather than silently
    misinterpreting a string of the wrong kind.
    """
    bad_edge = [t for t in edge_targets if len(t) != 4]
    bad_corner = [t for t in corner_targets if len(t) != 6]
    if bad_edge:
        raise ValueError(
            f"edge_targets must all be 4-char strings; got: {bad_edge[:5]}"
        )
    if bad_corner:
        raise ValueError(
            f"corner_targets must all be 6-char strings; got: {bad_corner[:5]}"
        )

    if seed is not None:
        random.seed(seed)

    has_parity = random.random() < 0.5

    c_perm, c_ori, c_cycles, c_req, c_links = generate_corner_scramble_state(
        corner_targets,
        min_pairs=corner_min_pairs,
        force_parity=(1 if has_parity else 0),
    )

    # Edges are ALWAYS generated as the standard, always-even-parity case --
    # no special exclusion for UR. If corners have parity, find wherever
    # the UF-piece (cubie 0) and UR-piece (cubie 2) actually ended up and
    # swap THOSE positions' contents -- not positions 0 and 2 themselves.
    # That single transposition flips the edge permutation from even to odd
    # (matching corners) while leaving the orientation SUM unchanged (still
    # even, since swapping which position holds which value doesn't change
    # the sum) -- the pseudo-swap convention.
    e_perm, e_ori, e_cycles, e_req, e_links = cube.generate_scramble_state(
        edge_targets, min_pairs=edge_min_pairs
    )
    e_perm, e_ori = list(e_perm), list(e_ori)
    if has_parity:
        pos_of_uf_piece = e_perm.index(0)
        pos_of_ur_piece = e_perm.index(2)
        e_perm[pos_of_uf_piece], e_perm[pos_of_ur_piece] = (
            e_perm[pos_of_ur_piece],
            e_perm[pos_of_uf_piece],
        )
        e_ori[pos_of_uf_piece], e_ori[pos_of_ur_piece] = (
            e_ori[pos_of_ur_piece],
            e_ori[pos_of_uf_piece],
        )

    facelet_string = build_facelet_string(e_perm, e_ori, c_perm, c_ori)

    return {
        "facelet_string": facelet_string,
        "has_parity": has_parity,
        "edge_perm": e_perm,
        "edge_ori": e_ori,
        "edge_cycles": e_cycles,
        "edge_requirements": e_req,
        "edge_target_links": e_links,
        "corner_perm": c_perm,
        "corner_ori": c_ori,
        "corner_cycles": c_cycles,
        "corner_requirements": c_req,
        "corner_target_links": c_links,
    }


if __name__ == "__main__":
    beginning = time.time_ns()

    # -- edge targets: 4-char letter-pair codes, e.g. "RURD" links the RU
    # position to the RD position (see Cube.LOC_TO_PERM_EDGE for the full
    # code -> position table). --
    edge_targets = {
        "RURD",
        "LUFD",
        "LBFD",
        "FLUB",
        "LBUR",
        "RUFL",
        "BLLF",
        "DFUL",
        "BURU",
        "FLDB",
        "BUUL",
        "LULD",
        "LULF",
        "LBUB",
        "DFLF",
        "BURB",
        "LULB",
        "FLFD",
        "LURB",
        "BLFL",
        "BUDR",
        "FLBU",
        "BLBU",
        "BUDB",
        "BLUR",
        "DFBU",
        "LBBU",
        "LUDF",
        "LBBD",
        "RULF",
        "RULD",
        "BUBL",
        "DFLU",
        "LBDB",
        "RUUB",
        "LURF",
        "BLFD",
        "DFUR",
        "BLRF",
        "BLRB",
        "LUBD",
        "LBRB",
        "DFFR",
        "LURU",
        "BUUR",
        "LUDR",
        "BLUL",
        "BLRU",
        "FLRD",
        "BLDL",
        "DFDL",
        "LUDL",
        "LBFL",
        "FLDR",
        "DFFL",
        "LBUL",
        "FLRB",
        "FLRF",
        "FLLB",
        "RUDL",
        "BLDR",
        "BUDL",
        "RURF",
        "RUDB",
        "BLLU",
        "DFDR",
        "LUUR",
        "FLBR",
        "LUBR",
        "LUBU",
        "FLLD",
        "BULF",
        "LBFR",
        "RUBL",
        "DFDB",
        "BUFL",
        "FLDL",
        "DFBL",
        "RUBU",
        "RUBD",
        "LBRF",
        "RURB",
        "DFRB",
        "RULB",
        "LBDF",
        "LBRD",
        "LBDL",
        "DFBD",
        "FLDF",
        "FLBD",
        "RULU",
        "LBDR",
        "FLBL",
        "LUDB",
        "FLLU",
        "RUDR",
        "BUFR",
        "BLBD",
        "LBBR",
        "BLDB",
        "RUDF",
        "BULD",
        "BLDF",
        "DFLD",
        "BURD",
        "BULB",
        "RUBR",
        "BLFR",
        "LUFR",
        "BUFD",
        "FLRU",
        "BLLD",
        "DFRF",
        "LURD",
        "RUFD",
        "BUBR",
        "BURF",
        "DFBR",
        "LBLU",
        "FLUR",
        "DFUB",
        "LBLF",
        "BLBR",
        "LUUB",
        "FLFR",
        "DFLB",
        "DFRU",
        "LUFL",
        "BUBD",
        "BUDF",
        "LUBL",
        "DFRD",
        "BLUB",
        "BLRD",
        "RUFR",
        "BULU",
        "FLUL",
        "LBLD",
        "RUUL",
    }

    # -- corner targets: 6-char strings, each two concatenated 3-letter
    # corner readings (see CORNER_ORI for the valid readings per position). --
    corner_targets = {
        "UFLBUR",
        "UBLDFR",
        "DFLDBR",
        "DBLUFL",
        "BURDFL",
        "UBLDBR",
        "DFRDBL",
        "UFLDBR",
    }

    ui = CLIInterface(
        output_mode=OutputMode.COLORED, log_to_file=True, log_level=logging.DEBUG
    )

    settings = Settings(ui)

    cube = Cube(
        "", ls=settings.letter_scheme, parity_swap_edges="UF-UR", can_parity_swap=True
    )

    state = generate_cube_state(
        cube, edge_targets, corner_targets, edge_min_pairs=3, corner_min_pairs=3
    )

    res = state["facelet_string"]
    print(res)
    print(f"has_parity: {state['has_parity']}")
    print("edge cycles:", state["edge_cycles"])
    print("corner cycles:", state["corner_cycles"])

    kociemba_solved_cube: str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    start = time.time_ns()
    scram = kociemba.solve(kociemba_solved_cube, res)

    print(f"Time: {(time.time_ns() - start) / 1e6:.2f}ms")
    print(scram)
    print(f"Total Time: {(time.time_ns() - beginning) / 1e6:.2f}ms")
