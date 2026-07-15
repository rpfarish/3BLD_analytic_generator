"""
BLD memo scramble generator (combined)
=======================================
This merges the logic of two previously-separate scripts:

  1. A standalone facelet-math generator: given BLD memo "target pairs"
     (buffer-based letter chains for edges/corners), it works out the
     *exact* resulting cube permutation/orientation and renders it as a
     54-char Kociemba-style facelet string. Pure algebra, no dependencies
     beyond the standard library.

  2. `cube.py`'s `Cube` class: a live move-based cube simulator whose
     `solve(invert=True)` method calls
         kociemba.solve(SOLVED_FACELETS, current_facelets)
     to turn a *facelet state* into an actual, turnable WCA-notation
     scramble. That class also does memo-driven scrambling, but via a
     different, heavier path (executing one physical commutator per
     memo pair, using project-local `comms`/`dlin`/`Settings`/
     `LetterScheme` modules that aren't available here).

The overlap between the two files is exactly "facelet string <-> real
scramble moves", so that's the seam this module combines them on:
generator (1) computes the *exact* target facelet string from memo
pairs, and the `kociemba` two-argument solve -- the same call
`Cube.solve(invert=True)` makes -- turns that facelet string into an
actual scramble algorithm you could hand to a solver.

Everything from file 1 (letter scheme, chain validation, cycle
assembly, orientation filling, parity fixing, facelet-string
construction) is unchanged below. The only new logic is
`scramble_algorithm_from_facelets()` plus the wiring that calls it from
`generate_scramble()` / `generate_until_exhausted()`.
"""

import random

import kociemba

# ----------------------------------------------------------------------
# 1. Facelet index tables (standard Kociemba cubie<->facelet mapping)
# ----------------------------------------------------------------------

FACE_BASE = {"U": 0, "R": 9, "F": 18, "D": 27, "L": 36, "B": 45}

CORNER_SLOTS = ["URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB"]
CORNER_FACELETS = {
    "URF": (8, 9, 20),
    "UFL": (6, 18, 38),
    "ULB": (0, 36, 47),
    "UBR": (2, 45, 11),
    "DFR": (29, 26, 15),
    "DLF": (27, 44, 24),
    "DBL": (33, 53, 42),
    "DRB": (35, 17, 51),
}
CORNER_COLORS = {
    name: tuple(name) for name in CORNER_SLOTS
}  # e.g. URF -> ('U','R','F')

EDGE_SLOTS = ["UR", "UF", "UL", "UB", "DR", "DF", "DL", "DB", "FR", "FL", "BL", "BR"]
EDGE_FACELETS = {
    "UR": (5, 10),
    "UF": (7, 19),
    "UL": (3, 37),
    "UB": (1, 46),
    "DR": (32, 16),
    "DF": (28, 25),
    "DL": (30, 43),
    "DB": (34, 52),
    "FR": (23, 12),
    "FL": (21, 41),
    "BL": (50, 39),
    "BR": (48, 14),
}
EDGE_COLORS = {name: tuple(name) for name in EDGE_SLOTS}  # e.g. UR -> ('U','R')

EDGE_BUFFER = "UF"
CORNER_BUFFER = "URF"

# Kociemba's own solved-state string, in the same U R F D L B order used
# throughout this file -- this is identical to `Cube.kociemba_solved_cube`
# in cube.py, which is what makes the two-argument kociemba.solve() call
# below a drop-in equivalent of `Cube.solve(invert=True)`.
SOLVED_FACELETS = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

# ----------------------------------------------------------------------
# 2. Letter scheme: letter -> (slot, side)
# ----------------------------------------------------------------------

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWX"  # 24 letters


def build_letter_scheme(slots, sides_per_slot):
    letter_to_loc = {}
    loc_to_letter = {}
    i = 0
    for slot in slots:
        for side in range(sides_per_slot):
            letter = ALPHABET[i]
            letter_to_loc[letter] = (slot, side)
            loc_to_letter[(slot, side)] = letter
            i += 1
    return letter_to_loc, loc_to_letter


EDGE_LETTER_TO_LOC, EDGE_LOC_TO_LETTER = build_letter_scheme(EDGE_SLOTS, 2)
CORNER_LETTER_TO_LOC, CORNER_LOC_TO_LETTER = build_letter_scheme(CORNER_SLOTS, 3)


def print_letter_scheme():
    print("=== EDGE letters (buffer = UF) ===")
    for slot in EDGE_SLOTS:
        colors = EDGE_COLORS[slot]
        letters = [EDGE_LOC_TO_LETTER[(slot, s)] for s in range(2)]
        tag = "  <- BUFFER" if slot == EDGE_BUFFER else ""
        print(
            f"  {slot}: side0(on {colors[0]})={letters[0]}  "
            f"side1(on {colors[1]})={letters[1]}{tag}"
        )

    print("\n=== CORNER letters (buffer = URF) ===")
    for slot in CORNER_SLOTS:
        colors = CORNER_COLORS[slot]
        letters = [CORNER_LOC_TO_LETTER[(slot, s)] for s in range(3)]
        tag = "  <- BUFFER" if slot == CORNER_BUFFER else ""
        print(
            f"  {slot}: side0(on {colors[0]})={letters[0]}  "
            f"side1(on {colors[1]})={letters[1]}  "
            f"side2(on {colors[2]})={letters[2]}{tag}"
        )

    print("\n=== Letters grouped by face ===")
    for face in "URFDLB":
        hits = []
        for letter, (slot, side) in EDGE_LETTER_TO_LOC.items():
            if EDGE_COLORS[slot][side] == face:
                hits.append(f"{letter}(edge {slot})")
        for letter, (slot, side) in CORNER_LETTER_TO_LOC.items():
            if CORNER_COLORS[slot][side] == face:
                hits.append(f"{letter}(corner {slot})")
        print(f"  {face}: {', '.join(sorted(hits))}")


# ----------------------------------------------------------------------
# 3. Target pairs -> chains, validated against reuse
# ----------------------------------------------------------------------


def chains_from_pairs(pairs, letter_to_loc, buffer_slot):
    """pairs: list of (X,Y) strings/letters that must appear consecutively.
    Returns list of chains (each a list of letters in order)."""
    nxt = {}
    used_as_source = set()
    for a, b in pairs:
        if a not in letter_to_loc or b not in letter_to_loc:
            raise ValueError(f"Unknown letter in pair ({a},{b})")
        if a in used_as_source:
            raise ValueError(
                f"Letter {a} used as first-of-pair twice; "
                f"not a valid single permutation"
            )
        if letter_to_loc[a][0] == buffer_slot or letter_to_loc[b][0] == buffer_slot:
            raise ValueError(
                f"Pair ({a},{b}) references the buffer's own "
                f"letters -- buffer letters can't be targeted"
            )
        nxt[a] = b
        used_as_source.add(a)

    targets = {b for _, b in pairs}
    starts = [a for a, _ in pairs if a not in targets]

    chains = []
    seen = set()
    for s in starts:
        if s in seen:
            continue
        chain = [s]
        seen.add(s)
        cur = s
        while cur in nxt:
            cur = nxt[cur]
            if cur in seen:
                raise ValueError(f"Cycle detected inside target pairs at {cur}")
            chain.append(cur)
            seen.add(cur)
        chains.append(chain)

    # validate: no slot appears twice across all target chains
    slot_uses = {}
    for chain in chains:
        for letter in chain:
            slot = letter_to_loc[letter][0]
            if slot in slot_uses:
                raise ValueError(
                    f"Slot {slot} referenced by both {slot_uses[slot]} and "
                    f"{letter} -- a slot can only be used once"
                )
            slot_uses[slot] = letter
    return chains


# ----------------------------------------------------------------------
# 4. Assemble target chains + random filler into full cycle structure
#    (Chinese-Restaurant-Process style: gives correct uniform distribution
#    AND a realistic random number of cycle breaks)
# ----------------------------------------------------------------------


def assemble_cycles(
    target_chains, all_slots, letter_to_loc, loc_to_letter, buffer_slot
):
    used_slots = {letter_to_loc[l][0] for chain in target_chains for l in chain}
    free_slots = [s for s in all_slots if s not in used_slots and s != buffer_slot]

    # filler tokens: singleton letters for each free slot, at a RANDOM side
    # (side doesn't matter for filler -- it'll get randomized/fixed anyway)
    filler_tokens = [
        [loc_to_letter[(s, random.randrange(3 if all_slots is CORNER_SLOTS else 2))]]
        for s in free_slots
    ]

    tokens = [list(c) for c in target_chains] + filler_tokens
    random.shuffle(tokens)

    cycles = [[tokens[0]]]
    placed = len(tokens[0])
    for token in tokens[1:]:
        r = random.randrange(placed + 1)
        if r == placed:
            cycles.append([token])  # cycle break
        else:
            flat = 0
            inserted = False
            for cyc in cycles:
                for ti, tk in enumerate(cyc):
                    if flat <= r < flat + len(tk):
                        cyc.insert(ti + 1, token)
                        inserted = True
                        break
                    flat += len(tk)
                if inserted:
                    break
        placed += len(token)

    return [[l for tk in cyc for l in tk] for cyc in cycles]


# ----------------------------------------------------------------------
# 5. Build occupant / orientation arrays from the assembled cycles
# ----------------------------------------------------------------------


def build_state(cycles, letter_to_loc, buffer_slot, mod):
    occupant = {}
    orient = {}
    all_slots_hit = set()

    for i, cyc in enumerate(cycles):
        prev = buffer_slot if i == 0 else None
        if i > 0:
            # a real cycle break happens here (buffer_letter, first-of-cyc)
            # the first-of-cyc's slot becomes the new "prev" origin, and the
            # PIECE now homed at the buffer slot moves here -- mirror the
            # i==0 handling by just starting prev at buffer_slot again,
            # since after a break you conceptually re-anchor at the buffer.
            prev = buffer_slot
            # NOTE: if buffer_slot's occupant was already set by an earlier
            # cycle this would be a conflict; free cycles must NOT reuse it.
            # We instead treat free cycles as self-closing (see below) and
            # only use `prev=buffer_slot` bookkeeping for the FIRST cycle.
        if i == 0:
            for letter in cyc:
                slot, side = letter_to_loc[letter]
                occupant[prev] = slot
                orient[prev] = side
                all_slots_hit.add(prev)
                prev = slot
            occupant[prev] = buffer_slot
            all_slots_hit.add(prev)
            # orientation of this last piece (the one homed at buffer) is
            # not target-constrained; fill in later
        else:
            # free, self-closing cycle -- not attached to the buffer at all
            slots = [letter_to_loc[l][0] for l in cyc]
            sides = [letter_to_loc[l][1] for l in cyc]
            n = len(slots)
            for k in range(n):
                occupant[slots[k]] = slots[(k + 1) % n]
                orient[slots[k]] = sides[(k + 1) % n]
                all_slots_hit.add(slots[k])

    return occupant, orient, all_slots_hit


# ----------------------------------------------------------------------
# 6. Fill remaining slots uniformly at random, fix orientation-sum parity
# ----------------------------------------------------------------------


def permutation_parity(occupant, slots):
    seen = set()
    swaps = 0
    for s in slots:
        if s in seen:
            continue
        cur = s
        length = 0
        while cur not in seen:
            seen.add(cur)
            cur = occupant[cur]
            length += 1
        swaps += length - 1
    return swaps % 2


def complete_state(
    occupant, orient, hit_slots, all_slots, buffer_slot, mod, target_locked_slots
):
    free = [s for s in all_slots if s not in hit_slots]
    pieces = free[:]
    random.shuffle(pieces)
    for slot, piece in zip(free, pieces):
        occupant[slot] = piece

    # fill orientation for any slot that has occupant but no orient yet
    unset_orient_slots = [s for s in all_slots if s not in orient]
    running = 0
    for s in unset_orient_slots[:-1] if unset_orient_slots else []:
        v = random.randrange(mod)
        orient[s] = v
        running += v
    if unset_orient_slots:
        last = unset_orient_slots[-1]
        # force sum(orient) % mod == 0 overall
        current_sum = sum(orient.values()) - orient.get(last, 0)
        orient[last] = (-current_sum) % mod

    return occupant


def fix_parity(occupant, orient, all_slots, protected_slots, target_parity):
    if permutation_parity(occupant, all_slots) == target_parity:
        return
    candidates = [s for s in all_slots if s not in protected_slots]
    if len(candidates) < 2:
        raise RuntimeError(
            "Not enough free slots to fix parity -- "
            "loosen target pairs or use bigger free pool"
        )
    a, b = random.sample(candidates, 2)
    # Swap occupant AND orient together as coupled pairs -- otherwise a
    # slot's (destination, side) reading can land on the wrong slot and
    # silently corrupt which letter is spoken there (this can even corrupt
    # a target pair's incoming letter if the swap lands on its predecessor).
    occupant[a], occupant[b] = occupant[b], occupant[a]
    orient[a], orient[b] = orient[b], orient[a]


# ----------------------------------------------------------------------
# 7. Facelet string construction
# ----------------------------------------------------------------------


def build_facelet_string(edge_occupant, edge_orient, corner_occupant, corner_orient):
    facelets = ["?"] * 54
    for face, base in FACE_BASE.items():
        facelets[base + 4] = face  # centers fixed

    for slot in EDGE_SLOTS:
        home = edge_occupant[slot]
        o = edge_orient[slot]
        natural = EDGE_COLORS[home]
        idxs = EDGE_FACELETS[slot]
        for i in range(2):
            facelets[idxs[i]] = natural[(i - o) % 2]

    for slot in CORNER_SLOTS:
        home = corner_occupant[slot]
        t = corner_orient[slot]
        natural = CORNER_COLORS[home]
        idxs = CORNER_FACELETS[slot]
        for i in range(3):
            facelets[idxs[i]] = natural[(i - t) % 3]

    return "".join(facelets)


# ----------------------------------------------------------------------
# 8. NEW: facelets -> real scramble moves
#    (this is cube.py's `Cube.solve(invert=True)` logic, lifted out so it
#    can run on a facelet string directly, without needing a live Cube /
#    dlin / comms / Settings / LetterScheme instance)
# ----------------------------------------------------------------------


def scramble_algorithm_from_facelets(facelets, max_depth=24):
    """Return a WCA-notation move sequence that turns a solved cube into
    `facelets`.

    Equivalent to `Cube.solve(invert=True)` in cube.py, which calls
        kociemba.solve(self.kociemba_solved_cube, self.get_faces_colors())
    i.e. "solve" FROM the solved state TO the current state -- which is
    exactly a scramble. Here `facelets` (produced by build_facelet_string)
    stands in for `self.get_faces_colors()`.
    """
    return kociemba.solve(SOLVED_FACELETS, facelets, max_depth=max_depth)


# ----------------------------------------------------------------------
# 9. Top-level: generate one scramble from target pairs
# ----------------------------------------------------------------------


def generate_scramble(
    edge_target_pairs, corner_target_pairs, verbose=True, include_algorithm=True
):
    edge_chains = chains_from_pairs(edge_target_pairs, EDGE_LETTER_TO_LOC, EDGE_BUFFER)
    corner_chains = chains_from_pairs(
        corner_target_pairs, CORNER_LETTER_TO_LOC, CORNER_BUFFER
    )

    edge_cycles = assemble_cycles(
        edge_chains, EDGE_SLOTS, EDGE_LETTER_TO_LOC, EDGE_LOC_TO_LETTER, EDGE_BUFFER
    )
    corner_cycles = assemble_cycles(
        corner_chains,
        CORNER_SLOTS,
        CORNER_LETTER_TO_LOC,
        CORNER_LOC_TO_LETTER,
        CORNER_BUFFER,
    )

    edge_occ, edge_or, edge_hit = build_state(
        edge_cycles, EDGE_LETTER_TO_LOC, EDGE_BUFFER, 2
    )
    corner_occ, corner_or, corner_hit = build_state(
        corner_cycles, CORNER_LETTER_TO_LOC, CORNER_BUFFER, 3
    )

    target_edge_slots = {EDGE_LETTER_TO_LOC[l][0] for c in edge_chains for l in c}
    target_corner_slots = {CORNER_LETTER_TO_LOC[l][0] for c in corner_chains for l in c}

    complete_state(
        edge_occ, edge_or, edge_hit, EDGE_SLOTS, EDGE_BUFFER, 2, target_edge_slots
    )
    complete_state(
        corner_occ,
        corner_or,
        corner_hit,
        CORNER_SLOTS,
        CORNER_BUFFER,
        3,
        target_corner_slots,
    )

    edge_parity = permutation_parity(edge_occ, EDGE_SLOTS)
    corner_parity = permutation_parity(corner_occ, CORNER_SLOTS)
    if edge_parity != corner_parity:
        # classic UF/UR-style swap: fix on whichever side has free (non-target) slots
        free_edges = [s for s in EDGE_SLOTS if s not in target_edge_slots]
        if len(free_edges) >= 2:
            fix_parity(edge_occ, edge_or, EDGE_SLOTS, target_edge_slots, corner_parity)
        else:
            fix_parity(
                corner_occ, corner_or, CORNER_SLOTS, target_corner_slots, edge_parity
            )

    facelets = build_facelet_string(edge_occ, edge_or, corner_occ, corner_or)

    algorithm = (
        scramble_algorithm_from_facelets(facelets) if include_algorithm else None
    )

    if verbose:
        print("Edge cycles (letters spoken, cycle-break = new line):")
        for c in edge_cycles:
            print("   " + " ".join(c))
        print("Corner cycles:")
        for c in corner_cycles:
            print("   " + " ".join(c))
        print(
            f"edge parity={edge_parity}  corner parity={corner_parity} (post-fix should match)"
        )
        if algorithm is not None:
            print(f"scramble algorithm: {algorithm}")

    return facelets, edge_occ, edge_or, corner_occ, corner_or, algorithm


def generate_until_exhausted(
    master_edge_pairs, master_corner_pairs, edge_batch=3, corner_batch=2, verbose=False
):
    """Keep generating scrambles, each drilling a batch of yet-unused target
    pairs, until every pair in both master lists has appeared at least once.
    Returns a list of (facelets, algorithm, edge_pairs_used, corner_pairs_used)."""
    remaining_edges = list(master_edge_pairs)
    remaining_corners = list(master_corner_pairs)
    results = []

    while remaining_edges or remaining_corners:
        e_batch = remaining_edges[:edge_batch]
        remaining_edges = remaining_edges[edge_batch:]
        c_batch = remaining_corners[:corner_batch]
        remaining_corners = remaining_corners[corner_batch:]

        facelets, *_, algorithm = generate_scramble(e_batch, c_batch, verbose=verbose)
        results.append((facelets, algorithm, e_batch, c_batch))

    return results


if __name__ == "__main__":
    print_letter_scheme()

    print("\n--- single scramble ---")
    # (buffer letters C/D for edges and A/B/C for corners can't be targeted)
    edge_targets = [("A", "H"), ("H", "N")]  # edge chain A->H->N
    corner_targets = [("D", "H")]  # corner chain D->H
    facelets, eo, eor, co, cor_, algorithm = generate_scramble(
        edge_targets, corner_targets
    )
    print("Facelet string:")
    print(facelets)
    print("Scramble algorithm (apply to a solved cube):")
    print(" ", algorithm)
    assert len(facelets) == 54 and "?" not in facelets

    print("\n--- batch mode over a master pair list ---")
    master_edges = [("A", "H"), ("H", "N"), ("E", "I"), ("W", "L")]
    master_corners = [("D", "H"), ("K", "Q")]
    for i, (fl, alg, e_used, c_used) in enumerate(
        generate_until_exhausted(
            master_edges, master_corners, edge_batch=2, corner_batch=1
        )
    ):
        print(f"scramble {i + 1}: edges={e_used} corners={c_used}")
        print(f"  facelets:  {fl}")
        print(f"  algorithm: {alg}")
