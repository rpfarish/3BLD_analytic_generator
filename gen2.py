"""
BLD memo scramble generator, wired to a real letter scheme
============================================================
This is the facelet-math scramble generator (target memo pairs -> exact
cube state -> real WCA scramble via `kociemba.solve`) combined with the
project's actual `LetterScheme` class and `settings.json`, instead of the
generator's own placeholder A-X scheme.

What changed vs. the standalone generator
------------------------------------------
The standalone version invents its own letters by walking EDGE_SLOTS /
CORNER_SLOTS in a fixed order and stamping A, B, C, ... onto them
(`build_letter_scheme`). That's fine for a self-contained demo, but it
has nothing to do with any real speffz-style scheme someone actually has
memorized.

Here, `letter_scheme_from_settings()` builds the exact same kind of
`{letter: (slot, side)}` tables the generator needs, but reads them out of
`settings.json`'s `letter_scheme` block (loaded/validated via the real
`LetterScheme` class from `Letterscheme/letterscheme.py`) and the real
`buffers` block, so `A`, `H`, `N`, ... below mean whatever they mean on
your sheet, not an arbitrary A-X walk.

`settings.json`'s `parity_swap_edges` ("UF-UR") is also wired in: when a
parity fix is needed, `fix_parity` now tries that specific edge pair
first (the way BLD solvers conventionally do a fixed pseudo-swap),
falling back to a random pair only if that pair is unavailable (e.g.
because one of its slots is itself a memo target).

Everything else -- chain validation, cycle assembly, orientation filling,
parity detection, facelet-string construction, and the
facelets -> `kociemba.solve` scramble step -- is the unmodified algebra
from the standalone generator.

`comm_files` / `floating_comms_sheet_name` / `drill_show_comms` in
settings.json are about spreadsheet-driven commutator lookup (the
`Settings` class's job) and aren't used here -- this module only cares
about `letter_scheme`, `buffers`, and `parity_swap_edges`.
"""

import json
import random
from pathlib import Path

import kociemba

from Letterscheme.letterscheme import LetterScheme

# ----------------------------------------------------------------------
# 1. Facelet index tables (standard Kociemba cubie<->facelet mapping)
#    -- unchanged from the standalone generator, these are fixed by the
#    Kociemba facelet convention, not by anyone's letter scheme.
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

SOLVED_FACELETS = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

# ----------------------------------------------------------------------
# 2. Real letter scheme, loaded from settings.json via LetterScheme
#    (replaces the standalone generator's `build_letter_scheme`)
# ----------------------------------------------------------------------


def _face_set_maps():
    """slot's face-set (e.g. frozenset('U','R','F')) -> canonical slot name"""
    edge_map = {frozenset(slot): slot for slot in EDGE_SLOTS}
    corner_map = {frozenset(slot): slot for slot in CORNER_SLOTS}
    return edge_map, corner_map


def letter_scheme_from_settings(settings_path="settings.json"):
    """Read settings.json's letter_scheme/buffers/parity_swap_edges and turn
    them into the {letter: (canonical_slot, side)} tables the rest of this
    module works with.

    `settings.json` positions like "FU" or "UFR"/"RUF" describe a piece by
    *which face's sticker* the letter sits on (the orientation), using
    whatever face-name order someone's sheet happens to use. This module's
    facelet tables (CORNER_FACELETS / EDGE_FACELETS above) fix one
    canonical name per physical slot (e.g. always "URF", never "RUF"). So
    for each raw position we look up its physical slot by face-set, and
    record `side` = index of the raw position's first face within that
    canonical slot name -- exactly mirroring what the standalone
    generator's own `build_letter_scheme` produced, just sourced from real
    data instead of an A-X walk.
    """
    with Path(settings_path).open(encoding="utf-8") as f:
        settings = json.load(f)

    raw_scheme = {
        pos.upper(): name.upper() for pos, name in settings["letter_scheme"].items()
    }
    # Validates there are exactly 48 entries and builds letter->pos reverse maps.
    letter_scheme_obj = LetterScheme(ltr_scheme=raw_scheme)

    edge_faces, corner_faces = _face_set_maps()

    edge_letter_to_loc, edge_loc_to_letter = {}, {}
    corner_letter_to_loc, corner_loc_to_letter = {}, {}

    for pos, letter in raw_scheme.items():
        faces = frozenset(pos)
        if len(pos) == 2:
            slot = edge_faces[faces]
            side = slot.index(pos[0])
            edge_letter_to_loc[letter] = (slot, side)
            edge_loc_to_letter[(slot, side)] = letter
        elif len(pos) == 3:
            slot = corner_faces[faces]
            side = slot.index(pos[0])
            corner_letter_to_loc[letter] = (slot, side)
            corner_loc_to_letter[(slot, side)] = letter
        else:
            raise ValueError(f"Unexpected position '{pos}' in letter_scheme")

    edge_buffer_raw = settings["buffers"]["edge_buffer"].upper()
    corner_buffer_raw = settings["buffers"]["corner_buffer"].upper()
    edge_buffer = edge_faces[frozenset(edge_buffer_raw)]
    corner_buffer = corner_faces[frozenset(corner_buffer_raw)]

    parity_swap_slots = None
    parity_swap_raw = settings.get("parity_swap_edges", "")
    if parity_swap_raw and "-" in parity_swap_raw:
        a_raw, b_raw = (p.upper() for p in parity_swap_raw.split("-"))
        parity_swap_slots = (edge_faces[frozenset(a_raw)], edge_faces[frozenset(b_raw)])

    return {
        "letter_scheme_obj": letter_scheme_obj,
        "edge_letter_to_loc": edge_letter_to_loc,
        "edge_loc_to_letter": edge_loc_to_letter,
        "corner_letter_to_loc": corner_letter_to_loc,
        "corner_loc_to_letter": corner_loc_to_letter,
        "edge_buffer": edge_buffer,
        "corner_buffer": corner_buffer,
        "parity_swap_slots": parity_swap_slots,
    }


def print_letter_scheme(scheme):
    edge_l2l = scheme["edge_letter_to_loc"]
    corner_l2l = scheme["corner_letter_to_loc"]
    edge_buffer = scheme["edge_buffer"]
    corner_buffer = scheme["corner_buffer"]

    print("=== EDGE letters (buffer = %s) ===" % edge_buffer)
    for slot in EDGE_SLOTS:
        colors = EDGE_COLORS[slot]
        letters = [scheme["edge_loc_to_letter"][(slot, s)] for s in range(2)]
        tag = "  <- BUFFER" if slot == edge_buffer else ""
        print(
            f"  {slot}: side0(on {colors[0]})={letters[0]}  "
            f"side1(on {colors[1]})={letters[1]}{tag}"
        )

    print("\n=== CORNER letters (buffer = %s) ===" % corner_buffer)
    for slot in CORNER_SLOTS:
        colors = CORNER_COLORS[slot]
        letters = [scheme["corner_loc_to_letter"][(slot, s)] for s in range(3)]
        tag = "  <- BUFFER" if slot == corner_buffer else ""
        print(
            f"  {slot}: side0(on {colors[0]})={letters[0]}  "
            f"side1(on {colors[1]})={letters[1]}  "
            f"side2(on {colors[2]})={letters[2]}{tag}"
        )


# ----------------------------------------------------------------------
# 3. Target pairs -> chains, validated against reuse
#    -- unchanged algebra from the standalone generator
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
#    -- unchanged algebra from the standalone generator
# ----------------------------------------------------------------------


def assemble_cycles(
    target_chains, all_slots, letter_to_loc, loc_to_letter, buffer_slot
):
    used_slots = {letter_to_loc[l][0] for chain in target_chains for l in chain}
    free_slots = [s for s in all_slots if s not in used_slots and s != buffer_slot]

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
#    -- unchanged algebra from the standalone generator
# ----------------------------------------------------------------------


def build_state(cycles, letter_to_loc, buffer_slot, mod):
    occupant = {}
    orient = {}
    all_slots_hit = set()

    for i, cyc in enumerate(cycles):
        prev = buffer_slot if i == 0 else None
        if i > 0:
            prev = buffer_slot
        if i == 0:
            for letter in cyc:
                slot, side = letter_to_loc[letter]
                occupant[prev] = slot
                orient[prev] = side
                all_slots_hit.add(prev)
                prev = slot
            occupant[prev] = buffer_slot
            all_slots_hit.add(prev)
        else:
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
#    -- unchanged, except fix_parity now knows about parity_swap_edges
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

    unset_orient_slots = [s for s in all_slots if s not in orient]
    running = 0
    for s in unset_orient_slots[:-1] if unset_orient_slots else []:
        v = random.randrange(mod)
        orient[s] = v
        running += v
    if unset_orient_slots:
        last = unset_orient_slots[-1]
        current_sum = sum(orient.values()) - orient.get(last, 0)
        orient[last] = (-current_sum) % mod

    return occupant


def fix_parity(
    occupant, orient, all_slots, protected_slots, target_parity, preferred_pair=None
):
    """Same coupled occupant/orient swap as the standalone generator, but
    now tries settings.json's `parity_swap_edges` pair first (e.g. UF-UR),
    the way BLD solvers conventionally do a fixed pseudo-swap for parity,
    and only falls back to a random pair if that pair isn't usable (one of
    its slots is itself a memo target)."""
    if permutation_parity(occupant, all_slots) == target_parity:
        return

    if (
        preferred_pair is not None
        and preferred_pair[0] not in protected_slots
        and preferred_pair[1] not in protected_slots
    ):
        a, b = preferred_pair
    else:
        candidates = [s for s in all_slots if s not in protected_slots]
        if len(candidates) < 2:
            raise RuntimeError(
                "Not enough free slots to fix parity -- "
                "loosen target pairs or use bigger free pool"
            )
        a, b = random.sample(candidates, 2)

    occupant[a], occupant[b] = occupant[b], occupant[a]
    orient[a], orient[b] = orient[b], orient[a]


# ----------------------------------------------------------------------
# 7. Facelet string construction -- unchanged, only depends on the fixed
#    CORNER_SLOTS/EDGE_SLOTS/*_FACELETS tables, not the letter scheme.
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
# 8. facelets -> real scramble moves via kociemba.solve
# ----------------------------------------------------------------------


def scramble_algorithm_from_facelets(facelets, max_depth=24):
    return kociemba.solve(SOLVED_FACELETS, facelets, max_depth=max_depth)


# ----------------------------------------------------------------------
# 9. Top-level: generate one scramble from target pairs, using a real
#    letter scheme loaded from settings.json
# ----------------------------------------------------------------------


def generate_scramble(
    edge_target_pairs,
    corner_target_pairs,
    scheme=None,
    settings_path="settings.json",
    verbose=True,
    include_algorithm=True,
):
    if scheme is None:
        scheme = letter_scheme_from_settings(settings_path)

    edge_letter_to_loc = scheme["edge_letter_to_loc"]
    edge_loc_to_letter = scheme["edge_loc_to_letter"]
    corner_letter_to_loc = scheme["corner_letter_to_loc"]
    corner_loc_to_letter = scheme["corner_loc_to_letter"]
    edge_buffer = scheme["edge_buffer"]
    corner_buffer = scheme["corner_buffer"]
    parity_swap_slots = scheme["parity_swap_slots"]

    edge_chains = chains_from_pairs(edge_target_pairs, edge_letter_to_loc, edge_buffer)
    corner_chains = chains_from_pairs(
        corner_target_pairs, corner_letter_to_loc, corner_buffer
    )

    edge_cycles = assemble_cycles(
        edge_chains, EDGE_SLOTS, edge_letter_to_loc, edge_loc_to_letter, edge_buffer
    )
    corner_cycles = assemble_cycles(
        corner_chains,
        CORNER_SLOTS,
        corner_letter_to_loc,
        corner_loc_to_letter,
        corner_buffer,
    )

    edge_occ, edge_or, edge_hit = build_state(
        edge_cycles, edge_letter_to_loc, edge_buffer, 2
    )
    corner_occ, corner_or, corner_hit = build_state(
        corner_cycles, corner_letter_to_loc, corner_buffer, 3
    )

    target_edge_slots = {edge_letter_to_loc[l][0] for c in edge_chains for l in c}
    target_corner_slots = {corner_letter_to_loc[l][0] for c in corner_chains for l in c}

    complete_state(
        edge_occ, edge_or, edge_hit, EDGE_SLOTS, edge_buffer, 2, target_edge_slots
    )
    complete_state(
        corner_occ,
        corner_or,
        corner_hit,
        CORNER_SLOTS,
        corner_buffer,
        3,
        target_corner_slots,
    )

    edge_parity = permutation_parity(edge_occ, EDGE_SLOTS)
    corner_parity = permutation_parity(corner_occ, CORNER_SLOTS)
    if edge_parity != corner_parity:
        free_edges = [s for s in EDGE_SLOTS if s not in target_edge_slots]
        if len(free_edges) >= 2:
            fix_parity(
                edge_occ,
                edge_or,
                EDGE_SLOTS,
                target_edge_slots,
                corner_parity,
                preferred_pair=parity_swap_slots,
            )
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
    master_edge_pairs,
    master_corner_pairs,
    scheme=None,
    settings_path="settings.json",
    edge_batch=3,
    corner_batch=2,
    verbose=False,
):
    """Keep generating scrambles, each drilling a batch of yet-unused target
    pairs, until every pair in both master lists has appeared at least once."""
    if scheme is None:
        scheme = letter_scheme_from_settings(settings_path)

    remaining_edges = list(master_edge_pairs)
    remaining_corners = list(master_corner_pairs)
    results = []

    while remaining_edges or remaining_corners:
        e_batch = remaining_edges[:edge_batch]
        remaining_edges = remaining_edges[edge_batch:]
        c_batch = remaining_corners[:corner_batch]
        remaining_corners = remaining_corners[corner_batch:]

        facelets, *_, algorithm = generate_scramble(
            e_batch, c_batch, scheme=scheme, verbose=verbose
        )
        results.append((facelets, algorithm, e_batch, c_batch))

    return results


if __name__ == "__main__":
    scheme = letter_scheme_from_settings("settings.json")
    print_letter_scheme(scheme)

    print("\n--- single scramble (using the real settings.json scheme) ---")
    # Buffer letters ("U" for both edges and corners here -- UF/UFR) can't
    # be targeted, matching the note in chains_from_pairs.
    edge_targets = [("A", "H"), ("H", "N")]  # edge chain A->H->N
    corner_targets = [("D", "H")]  # corner chain D->H
    facelets, eo, eor, co, cor_, algorithm = generate_scramble(
        edge_targets, corner_targets, scheme=scheme
    )
    print("Facelet string:")
    print(facelets)
    print("Scramble algorithm (apply to a solved cube):")
    print(" ", algorithm)
    assert len(facelets) == 54 and "?" not in facelets

    print("\n--- batch mode over a master pair list ---")
    master_edges = [("A", "H"), ("H", "N"), ("E", "I"), ("W", "L")]
    master_corners = [("D", "H"), ("K", "L")]
    for i, (fl, alg, e_used, c_used) in enumerate(
        generate_until_exhausted(
            master_edges, master_corners, scheme=scheme, edge_batch=2, corner_batch=1
        )
    ):
        print(f"scramble {i + 1}: edges={e_used} corners={c_used}")
        print(f"  facelets:  {fl}")
        print(f"  algorithm: {alg}")
