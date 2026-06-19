from functools import reduce
from itertools import combinations

import dlin

# =============================================================================
# EDGE OPTIMIZER
# =============================================================================


def combine_types(type_a: int, type_b: int) -> int:
    """Combine two edge types using bitwise XOR on (orientation, parity)"""
    # Convert type 4 to type 2 (both represent flipped orientation)
    if type_a == 4:
        type_a = 2
    if type_b == 4:
        type_b = 2

    # Direct XOR and clamp to valid range [0,3]
    return (type_a ^ type_b) & 3


def get_edge_type(edge: dict[str, int]) -> int:
    """Get the type (0-4) of an edge based on orientation and parity"""
    if edge.get("type") == "misoriented":
        return 4

    # Direct bit packing: orientation is bit 1, parity is bit 0
    return (edge["orientation"] << 1) | edge["parity"]


def analyze_trace(trace, buffer_order=None):
    """
    Analyze any trace and find optimal edge cycle combinations.

    Args:
        trace: Dictionary containing 'edge' key with edge cycle data
        buffer_order: List of buffers in priority order. If None, uses all buffers from trace.

    Returns:
        Dictionary containing analysis results and optimal combinations
    """

    if buffer_order is None:
        print("Warning no buffer order provided...")
        buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]
        print("Defaulting to:", buffer_order)

    # Analyze edge types first
    edge_types = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for edge in trace["edge"]:
        edge_type = get_edge_type(edge)
        edge_types[edge_type] += 1

    # Validation checks
    sum_type_1_and_3 = edge_types[1] + edge_types[3]
    sum_type_2_3_and_4 = edge_types[2] + edge_types[3] + edge_types[4]

    is_valid = sum_type_1_and_3 % 2 == 0 and sum_type_2_3_and_4 % 2 == 0
    if is_valid:
        print("✓ All validation checks passed!")
    else:
        print("✗ Validation failed!")
        return None

    # Find optimal combinations
    results = find_optimal_combinations(trace["edge"], buffer_order)

    total_joins = 0
    total_targets = 0
    total_flips = 0

    for i, result in enumerate(results, 1):
        if "flips" in result and result["flips"]:
            total_flips += len(result["flips"])

        total_joins += result["joins"]
        total_targets += result["target_count"]

    all_targets = []
    all_flips = []
    for result in results:
        all_targets.extend(result["targets"])
        if "flips" in result:
            all_flips.extend(result["flips"])

    return {
        "edge_types": edge_types,
        "is_valid": is_valid,
        "combinations": results,
        "summary": {
            "total_groups": len(results),
            "total_joins": total_joins,
            "total_targets": total_targets,
            "total_flips": total_flips,
            "buffer_count": len([b for result in results for b in result["buffers"]]),
        },
        "target_sequence": all_targets,
        "flip_sequence": all_flips,
    }


def find_optimal_combinations(edges, buffer_order):
    """Find optimal way to combine ALL cycles to type 0 with maximum groups (minimum group sizes)"""

    # Create list of all edges with their types
    edge_data = []
    for edge in edges:
        edge_type = get_edge_type(edge)
        edge_data.append(
            {
                "buffer": edge["buffer"],
                "type": edge_type,
                "targets": edge["targets"],
                "edge": edge,
            }
        )

    # Separate type 0 cycles (already solved) from others
    type_0_cycles = [e for e in edge_data if e["type"] == 0]
    non_type_0_cycles = [e for e in edge_data if e["type"] != 0]

    results = []

    # Add type 0 cycles (no joins needed, but include buffer in targets)
    for cycle in type_0_cycles:
        results.append(
            {
                "buffers": [cycle["buffer"]],
                "targets": cycle["targets"],
                "flips": [],
                "joins": 0,
                "final_type": 0,
                "combination_path": [cycle["buffer"]],
                "target_count": len(cycle["targets"]),
            }
        )

    if not non_type_0_cycles:
        return results

    # Find optimal grouping of non-type 0 cycles (maximize number of groups)
    optimal_solution = find_maximum_groups(non_type_0_cycles, buffer_order)

    results.extend(optimal_solution)

    return results


def find_maximum_groups(cycles, buffer_order, all_sol=False):
    """Find maximum number of groups where each group combines to type 0 (prioritize smaller groups)"""

    n = len(cycles)
    if n == 0:
        return []

    # Try all possible groupings, starting with MOST groups (smallest group sizes)
    # This prioritizes solutions like [UF+FL, UB+UR] over [UF+UB+UR+FL]
    for num_groups in range(n, 0, -1):  # Count DOWN from max groups to 1
        solutions = find_groupings_with_n_groups(cycles, num_groups, buffer_order)
        if solutions:
            if len(solutions) > 1:
                print(solutions[1:])
            return solutions[0]

    return []


def flip_edge_piece(piece: str) -> str:
    """Flip an edge piece (UB -> BU, UR -> RU, etc.)"""
    if len(piece) == 2:
        return piece[1] + piece[0]
    return piece  # Return as-is if not a 2-letter edge piece


def find_groupings_with_n_groups(cycles, num_groups, buffer_order):
    """Find all ways to partition cycles into exactly num_groups where each group sums to type 0"""

    def backtrack(remaining_cycles, current_groups, target_groups):
        if len(current_groups) == target_groups:
            if not remaining_cycles:  # All cycles assigned
                return [current_groups[:]]
            else:
                return []

        if not remaining_cycles:
            return []

        solutions = []

        # For maximizing groups, prioritize smaller group sizes first
        max_size = min(
            len(remaining_cycles),
            len(remaining_cycles) - (target_groups - len(current_groups) - 1),
        )

        for group_size in range(1, max_size + 1):
            # Skip if not enough cycles left for remaining groups
            remaining_groups_needed = target_groups - len(current_groups) - 1
            cycles_after_this_group = len(remaining_cycles) - group_size

            if cycles_after_this_group < remaining_groups_needed:
                continue

            for group in combinations(remaining_cycles, group_size):
                # Check if this group combines to type 0
                if group_combines_to_type_0(group):
                    new_remaining = [c for c in remaining_cycles if c not in group]
                    new_groups = current_groups + [list(group)]
                    solutions.extend(
                        backtrack(new_remaining, new_groups, target_groups)
                    )

        return solutions

    solutions = backtrack(cycles, [], num_groups)
    # Convert to the expected format and sort by preference
    formatted_solutions = []
    for solution in solutions:
        formatted_groups = []
        total_joins = 0

        for group in solution:
            all_targets = []
            buffers = []
            flips = []  # Track misoriented edges separately

            # First add the primary buffer (first in buffer order)
            primary_buffer = min(
                group,
                key=lambda c: (
                    buffer_order.index(c["buffer"])
                    if c["buffer"] in buffer_order
                    else 999
                ),
            )
            buffers.append(primary_buffer["buffer"])

            if primary_buffer["type"] == 4:  # misoriented
                flips.append(primary_buffer["buffer"])
            else:
                all_targets.extend(primary_buffer["targets"])

            # Then add other buffers and their targets
            for cycle in group:
                if cycle == primary_buffer:
                    continue

                buffers.append(cycle["buffer"])
                if cycle["type"] == 4:
                    flips.append(cycle["buffer"])
                    continue

                # Add buffer to targets
                all_targets.append(cycle["buffer"])
                all_targets.extend(cycle["targets"])

                return_piece = cycle["buffer"]

                # Check if this cycle has flipped orientation
                if cycle["edge"].get("orientation", 0) == 1:
                    return_piece = flip_edge_piece(return_piece)

                all_targets.append(return_piece)

            joins_for_group = len(group) - 1  # n cycles need n-1 joins

            total_joins += joins_for_group

            formatted_groups.append(
                {
                    "buffers": buffers,
                    "targets": all_targets,
                    "flips": flips,
                    "joins": joins_for_group,
                    "final_type": 0,
                    "combination_path": buffers,
                    "target_count": len(all_targets),
                }
            )

        formatted_solutions.append((formatted_groups, total_joins))

    # Sort by total joins (ascending) to prefer solutions with fewer total joins
    # when multiple solutions have the same number of groups
    formatted_solutions.sort(key=lambda x: x[1])

    return [sol[0] for sol in formatted_solutions]


def group_combines_to_type_0(group) -> bool:
    """Check if a group of cycles combines to type 0"""
    if not group:
        return False

    types = [cycle["type"] for cycle in group]
    current_type = reduce(combine_types, types)

    return current_type == 0


# =============================================================================
# CORNER OPTIMIZER
# =============================================================================
#
# Corner cycle optimizer for Blindfolded (BLD) cubing on a 3×3×3 Rubik's Cube.
#
# Companion module to the existing edge optimizer.  The key differences from
# the edge case:
#
#   1. **Three orientations** — corners have CW (+1), correct (0), and CCW (−1)
#      orientations versus the two (flipped / correct) of edges.  Orientation
#      arithmetic uses Z/3Z (mod 3) rather than Z/2Z (XOR).
#
#   2. **Sticker rotation is geometry-specific** — for edges, flip_edge_piece
#      just reverses two characters.  For corners the mapping from one sticker
#      name to a rotated sticker name depends on which physical corner we are
#      dealing with.  The CORNER_ORI lookup table (derived from dlin's own
#      check_corner_symmetry helper) encodes this correctly.
#
#   3. **Parity constraint is relaxed for validation** — a parity scramble
#      (Rw/Uw wide moves) can produce a corner trace where the orientation sum
#      is 0 mod 3 but the parity count is odd.  This is a valid cube state;
#      the edge optimizer's parity swap handles the edge side of the equation.
#      We therefore validate *orientation only* for corners and fall back to an
#      orientation-only grouping strategy when no full type-0 partition exists.
#
# ─────────────────────────────────────────────────────────────────────────────
# dlin trace conventions for corners
# ─────────────────────────────────────────────────────────────────────────────
# Each entry in trace["corner"] is a dict:
#
#     {
#         "type":        "cycle" | "misoriented",
#         "buffer":      str,          # e.g. "UBL"  (U/D-first ⟹ oriented)
#         "targets":     list[str],    # empty for misoriented pieces
#         "orientation": int,          # 0 = correct, +1 = CW, -1 = CCW
#         "parity":      int,          # (len(targets)) % 2
#     }
#
# ─────────────────────────────────────────────────────────────────────────────
# Corner Type Encoding (6-type system)
# ─────────────────────────────────────────────────────────────────────────────
# type = orientation_z3 × 2 + parity
#
# where orientation_z3 = orientation % 3  (so −1 → 2, 0 → 0, +1 → 1)
#
#     ┌──────┬──────────────┬────────┐
#     │ type │ orientation  │ parity │
#     ├──────┼──────────────┼────────┤
#     │   0  │ 0  correct   │   0    │  ← already solved
#     │   1  │ 0  correct   │   1    │
#     │   2  │ 1  CW        │   0    │
#     │   3  │ 1  CW        │   1    │
#     │   4  │ 2  CCW (−1)  │   0    │
#     │   5  │ 2  CCW (−1)  │   1    │
#     └──────┴──────────────┴────────┘
#
# Combination: orientation adds mod 3, parity adds mod 2 (Z/3Z × Z/2Z).
#
# ─────────────────────────────────────────────────────────────────────────────
# Grouping strategy
# ─────────────────────────────────────────────────────────────────────────────
# Primary:  find groups where combined 6-type == 0 (both orientation and
#           parity cancel).  Works for all non-parity scrambles.
#
# Fallback: if no such partition exists (happens when a parity scramble
#           leaves an odd parity corner cycle with no partner), relax to
#           orientation-only grouping (combined orientation == 0 mod 3).
#           The caller is responsible for any resulting parity algorithm.


# ─────────────────────────────────────────────────────────────────────────────
# Sticker orientation lookup  (geometry source: dlin check_corner_symmetry)
# ─────────────────────────────────────────────────────────────────────────────

# Key   = sorted letters of any sticker belonging to that corner
# Value = [sticker_at_index_0, sticker_at_index_1, sticker_at_index_2]
# The sticker that starts with U or D is the "oriented" (correct) sticker.
CORNER_ORI: dict[str, list[str]] = {
    "BDL": ["LDB", "DBL", "BDL"],  # DBL is oriented  (index 1)
    "BDR": ["RDB", "BDR", "DBR"],  # DBR is oriented  (index 2)
    "BLU": ["LUB", "BUL", "UBL"],  # UBL is oriented  (index 2)
    "BRU": ["RUB", "UBR", "BUR"],  # UBR is oriented  (index 1)
    "DFL": ["LDF", "FDL", "DFL"],  # DFL is oriented  (index 2)
    "DFR": ["RDF", "DFR", "FDR"],  # DFR is oriented  (index 1)
    "FLU": ["LUF", "UFL", "FUL"],  # UFL is oriented  (index 1)
    "FRU": ["RUF", "FUR", "UFR"],  # UFR is oriented  (index 2)
}

NUM_CORNER_TYPES = 6  # Z/3Z × Z/2Z  (orientation × 2 + parity)

CORNER_TYPE_LABELS: dict[int, str] = {
    0: "correct-orientation, even-cycle (solved)",
    1: "correct-orientation, odd-cycle",
    2: "CW, even-cycle",
    3: "CW, odd-cycle",
    4: "CCW, even-cycle",
    5: "CCW, odd-cycle",
}


# ─────────────────────────────────────────────────────────────────────────────
# Sticker geometry helpers
# ─────────────────────────────────────────────────────────────────────────────


def corner_key(sticker: str) -> str:
    """
    Return the canonical CORNER_ORI lookup key for any sticker of a corner.

    >>> corner_key("UBL")
    'BLU'
    >>> corner_key("BUL")
    'BLU'
    """
    return "".join(sorted(sticker))


def rotate_corner_sticker(sticker: str, orientation: int) -> str:
    """
    Return the sticker name obtained by rotating *sticker* by *orientation*
    steps within its corner's sticker-index list.

    This is the corner analogue of flip_edge_piece for edges.  Unlike the edge
    case — where flipping is always a simple 2-character swap — the sticker
    rotation for corners is geometry-specific and cannot be derived from the
    characters alone.  CORNER_ORI encodes the correct mapping for each corner.

    Parameters
    ----------
    sticker : str
        Any 3-letter sticker name belonging to a corner, e.g. ``"UBL"``.
    orientation : int
        dlin orientation delta: 0 = no change, +1 = CW, −1 = CCW.

    Returns
    -------
    str
        The sticker at (current_index + orientation) % 3 in CORNER_ORI.

    Examples
    --------
    >>> rotate_corner_sticker("UBL", 0)
    'UBL'
    >>> rotate_corner_sticker("UBL", 1)    # CW  → index 2+1=0 → 'LUB'
    'LUB'
    >>> rotate_corner_sticker("UBL", -1)   # CCW → index 2-1=1 → 'BUL'
    'BUL'
    >>> rotate_corner_sticker("UFR", 1)    # CW  → index 2+1=0 → 'RUF'
    'RUF'
    >>> rotate_corner_sticker("UFR", -1)   # CCW → index 2-1=1 → 'FUR'
    'FUR'
    """
    if orientation == 0:
        return sticker
    key = corner_key(sticker)
    stickers = CORNER_ORI[key]
    current_index = stickers.index(sticker)
    return stickers[(current_index + orientation) % 3]


def get_oriented_sticker(sticker: str) -> str:
    """
    Return the correctly-oriented (U/D-first) sticker for the same corner.

    >>> get_oriented_sticker("BUL")
    'UBL'
    >>> get_oriented_sticker("UBL")
    'UBL'
    """
    key = corner_key(sticker)
    return next(s for s in CORNER_ORI[key] if s[0] in ("U", "D"))


# ─────────────────────────────────────────────────────────────────────────────
# Low-level type arithmetic  (Z/3Z × Z/2Z)
# ─────────────────────────────────────────────────────────────────────────────


def get_corner_type(corner: dict) -> int:
    """
    Encode a corner cycle dict as an integer type in [0, 5].

    dlin orientation field uses −1 (CCW), 0 (correct), +1 (CW).
    Python's % operator maps −1 → 2, so we use it directly.

    Returns  orientation_z3 * 2 + parity
    """
    orientation_z3 = corner.get("orientation", 0) % 3  # −1→2, 0→0, +1→1
    parity = corner.get("parity", 0)
    return orientation_z3 * 2 + parity


def decode_corner_type(ctype: int) -> tuple[int, int]:
    """
    Inverse of get_corner_type: return (orientation_z3, parity).

    >>> decode_corner_type(5)
    (2, 1)
    """
    return divmod(ctype, 2)  # → (orientation_z3, parity)


def combine_corner_types(type_a: int, type_b: int) -> int:
    """
    Combine two 6-types under Z/3Z × Z/2Z.

    Unlike the edge XOR trick (which works because both fields are Z/2Z),
    we must decode and re-encode because orientation lives in Z/3Z and
    parity lives in Z/2Z.

    Examples
    --------
    >>> combine_corner_types(2, 4)   # CW-even  + CCW-even  → correct-even
    0
    >>> combine_corner_types(1, 1)   # correct-odd + correct-odd → correct-even
    0
    >>> combine_corner_types(2, 2)   # CW-even  + CW-even   → CCW-even
    4
    >>> combine_corner_types(3, 5)   # CW-odd   + CCW-odd   → correct-even
    0
    """
    orient_a, parity_a = divmod(type_a, 2)
    orient_b, parity_b = divmod(type_b, 2)
    return ((orient_a + orient_b) % 3) * 2 + ((parity_a + parity_b) % 2)


# ─────────────────────────────────────────────────────────────────────────────
# Group validity checks  (strict and orientation-only fallback)
# ─────────────────────────────────────────────────────────────────────────────


def group_combines_to_type_0_corners(group) -> bool:
    """
    Return True iff all cycles in *group* combine to 6-type 0 (both
    orientation and parity cancel).

    Corner analogue of group_combines_to_type_0 for edges.
    """
    if not group:
        return False
    return reduce(combine_corner_types, [c["type"] for c in group]) == 0


def _group_orientation_sums_to_zero_corners(group) -> bool:
    """
    Fallback validity check: True iff the combined orientation (mod 3) is 0,
    ignoring parity.  Used when a full type-0 partition is impossible (parity
    scrambles).
    """
    if not group:
        return False
    orient_sum = sum(c["type"] // 2 for c in group) % 3
    return orient_sum == 0


# ─────────────────────────────────────────────────────────────────────────────
# Group result builder
# ─────────────────────────────────────────────────────────────────────────────


def _build_corner_group_result(group: list[dict], buffer_order: list[str]) -> dict:
    """
    Convert a validated group of corner cycles into the canonical result dict.

    Target-sequence construction
    ----------------------------
    Given a group {primary, c1, c2, …}:

        primary.targets                ← execute primary cycle as-is
        [c1.buffer]                    ← join: reach into c1's buffer slot
        c1.targets                     ← execute c1's cycle
        [rotate(c1.buffer, c1.orient)] ← return: close the join (twist-corrected)
        [c2.buffer] …

    "Misoriented" cycles (twisted at home, no targets) bypass the target
    block and accumulate in the ``flips`` list for separate handling.
    """
    all_targets: list[str] = []
    buffers: list[str] = []
    flips: list[str] = []  # twisted-in-place corners (corner analogue of edge flips)

    # ── Select primary buffer (highest priority in buffer_order) ────────────
    primary = min(
        group,
        key=lambda c: (
            buffer_order.index(c["buffer"]) if c["buffer"] in buffer_order else 999
        ),
    )
    buffers.append(primary["buffer"])

    if primary["corner"].get("type") == "misoriented":
        flips.append(primary["buffer"])
    else:
        all_targets.extend(primary["targets"])

    # ── Merge secondary cycles into the solve sequence ──────────────────────
    for cycle in group:
        if cycle is primary:
            continue

        buffers.append(cycle["buffer"])

        if cycle["corner"].get("type") == "misoriented":
            flips.append(cycle["buffer"])
            continue

        # Join sticker: target the secondary cycle's buffer slot
        all_targets.append(cycle["buffer"])
        # Execute the secondary cycle's own targets
        all_targets.extend(cycle["targets"])
        # Return sticker: rotate by the corner's orientation so the join
        # closes correctly regardless of how twisted the buffer piece is
        return_piece = rotate_corner_sticker(
            cycle["buffer"],
            cycle["corner"].get("orientation", 0),
        )
        all_targets.append(return_piece)

    return {
        "buffers": buffers,
        "targets": all_targets,
        "flips": flips,
        "joins": len(group) - 1,
        "final_type": 0,
        "combination_path": buffers,
        "target_count": len(all_targets),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Backtracking search
# ─────────────────────────────────────────────────────────────────────────────


def _buf_priority(buf: str | None, buffer_order: list[str]) -> int:
    """Return the buffer_order index of a buffer (lower = higher priority)."""
    print("BUFFER ORDER:", buffer_order)
    if buf and buf in buffer_order:
        return buffer_order.index(buf)
    return 999


def find_groupings_with_n_groups_corners(
    cycles: list[dict],
    num_groups: int,
    buffer_order: list[str],
    *,
    validity_fn=group_combines_to_type_0_corners,
) -> list[list[dict]]:

    # ── FIX: sort cycles by buffer priority BEFORE backtracking so that
    # combinations() explores higher-priority groupings first; this makes
    # the stable sort on total_joins below resolve ties in buffer-order's
    # favor instead of trace order's favor. ──
    cycles = sorted(cycles, key=lambda c: _buf_priority(c["buffer"], buffer_order))

    def backtrack(remaining: list, current_groups: list) -> list:
        if len(current_groups) == num_groups:
            return [current_groups[:]] if not remaining else []
        if not remaining:
            return []

        solutions = []
        groups_still_needed = num_groups - len(current_groups) - 1
        max_group_size = len(remaining) - groups_still_needed

        for group_size in range(1, max_group_size + 1):
            for group in combinations(remaining, group_size):
                if validity_fn(group):
                    new_remaining = [c for c in remaining if c not in group]
                    solutions.extend(
                        backtrack(new_remaining, current_groups + [list(group)])
                    )
        return solutions

    raw_solutions = backtrack(cycles, [])
    if not raw_solutions:
        return []

    formatted: list[tuple[list[dict], int]] = []
    for solution in raw_solutions:
        groups = [_build_corner_group_result(g, buffer_order) for g in solution]
        groups.sort(
            key=lambda g: _buf_priority(
                g["buffers"][0] if g["buffers"] else None, buffer_order
            )
        )
        total_joins = sum(g["joins"] for g in groups)
        formatted.append((groups, total_joins))

    formatted.sort(
        key=lambda x: (
            x[1],
            [
                _buf_priority(g["buffers"][0] if g["buffers"] else None, buffer_order)
                for g in x[0]
            ],
        )
    )
    return [sol[0] for sol in formatted]


def find_maximum_groups_corners(
    cycles: list[dict], buffer_order: list[str], all_sol: bool = False
) -> list[dict]:
    """
    Find the partition of *cycles* that maximises the number of valid groups.

    Corner analogue of find_maximum_groups for edges.

    Strategy
    --------
    1. **Strict pass** — require each group's combined 6-type == 0
       (orientation AND parity cancel).  This is the optimal case; it works
       for all non-parity scrambles.

    2. **Orientation-only fallback** — if no strict partition exists (e.g. a
       parity scramble leaves one odd-parity CCW cycle with no partner), relax
       the constraint to orientation-sum == 0 mod 3.  The caller must handle
       any remaining parity algorithm separately.
    """
    n = len(cycles)
    if n == 0:
        return []

    # ── Pass 1: strict (type-0) ──────────────────────────────────────────────
    for num_groups in range(n, 0, -1):
        solutions = find_groupings_with_n_groups_corners(
            cycles,
            num_groups,
            buffer_order,
            validity_fn=group_combines_to_type_0_corners,
        )
        if solutions:
            return solutions[0]

    # ── Pass 2: orientation-only fallback ────────────────────────────────────
    for num_groups in range(n, 0, -1):
        solutions = find_groupings_with_n_groups_corners(
            cycles,
            num_groups,
            buffer_order,
            validity_fn=_group_orientation_sums_to_zero_corners,
        )
        if solutions:
            return solutions[0]

    return []  # unreachable for a validated trace; defensive guard


# ─────────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────────


def find_optimal_combinations_corners(
    corners: list[dict], buffer_order: list[str]
) -> list[dict]:
    """
    Find the optimal way to combine ALL corner cycles into valid groups.

    Corner analogue of find_optimal_combinations for edges.

    Parameters
    ----------
    corners : list of dict
        Corner cycle entries from ``dlin.trace(…)["corner"]``.
        Required keys:
            buffer      – str   e.g. ``"UFR"``
            targets     – list[str]
            orientation – int   in {−1, 0, +1}
            parity      – int   in {0, 1}
            type        – str   ``"cycle"`` or ``"misoriented"``

    buffer_order : list of str
        Corner buffers in descending priority.

    Returns
    -------
    list of dict
        One result dict per group (keys mirror the edge result format):
            buffers          – list[str]  buffers in this group
            targets          – list[str]  ordered solve-target sequence
            flips            – list[str]  misoriented corners (separate handling)
            joins            – int        len(buffers) - 1
            final_type       – int        0
            combination_path – list[str]  same as buffers
            target_count     – int        len(targets)
    """
    corner_data: list[dict] = [
        {
            "buffer": c["buffer"],
            "type": get_corner_type(c),
            "targets": c["targets"],
            "corner": c,
        }
        for c in corners
    ]

    # Type-0: orientation=0, parity=0 → already fully solved, no joins needed
    type_0 = [c for c in corner_data if c["type"] == 0]
    non_type_0 = [c for c in corner_data if c["type"] != 0]

    results: list[dict] = []
    print("BUFFER ORDER:", buffer_order)

    for cycle in type_0:
        results.append(
            {
                "buffers": [cycle["buffer"]],
                "targets": cycle["targets"],
                "flips": [],
                "joins": 0,
                "final_type": 0,
                "combination_path": [cycle["buffer"]],
                "target_count": len(cycle["targets"]),
            }
        )

    if non_type_0:
        results.extend(find_maximum_groups_corners(non_type_0, buffer_order))

    return results


def analyze_corner_trace(
    trace: dict, buffer_order: list[str] | None = None
) -> dict | None:
    """
    Analyze a dlin corner trace and return optimal cycle-combination results.

    Corner analogue of analyze_trace for edges.

    Parameters
    ----------
    trace : dict
        Must contain key ``"corner"`` with corner cycle dicts from dlin.
    buffer_order : list of str, optional
        Corner buffer priority order.

    Returns
    -------
    dict or None
        None if validation fails (orientation sum ≠ 0 mod 3).

        On success (keys mirror the edge analyze_trace return value):
            corner_types    – dict[int, int]   6-type index → count
            is_valid        – bool
            combinations    – list of group result dicts
            summary         – aggregated statistics
            target_sequence – list[str]  all solve targets in order
            flip_sequence   – list[str]  all misoriented corner stickers

    Notes
    -----
    We validate **orientation only** (not parity).  A parity scramble can
    leave one odd-parity corner cycle with no partner — this is a valid cube
    state handled by the orientation-only fallback in find_maximum_groups_corners.
    """
    if buffer_order is None:
        print("Warning no buffer order provided...")
        buffer_order = ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"]
        print("Defaulting to:", buffer_order)

    # ── Type distribution ────────────────────────────────────────────────────
    corner_types: dict[int, int] = {t: 0 for t in range(NUM_CORNER_TYPES)}
    for corner in trace["corner"]:
        corner_types[get_corner_type(corner)] += 1

    # ── Validity: orientation sum only ───────────────────────────────────────
    # Each orientation=1 (CW) cycle contributes +1, each orientation=2 (CCW, i.e. -1)
    # contributes +2 ≡ −1 (mod 3).  Sum must be 0 mod 3 by the cube orientation law.
    orient_sum = (
        1 * (corner_types[2] + corner_types[3])  # orientation_z3 = 1  (CW)
        + 2 * (corner_types[4] + corner_types[5])  # orientation_z3 = 2  (CCW / −1)
    )
    is_valid = orient_sum % 3 == 0

    if is_valid:
        print("✓ All validation checks passed!")
    else:
        print(
            f"✗ Validation failed!  "
            f"orient_sum={orient_sum} mod 3 = {orient_sum % 3} (must be 0)"
        )
        return None

    # ── Optimal combinations ─────────────────────────────────────────────────
    results = find_optimal_combinations_corners(trace["corner"], buffer_order)

    total_joins = 0
    total_targets = 0
    total_flips = 0

    for i, result in enumerate(results, 1):
        if "flips" in result and result["flips"]:
            total_flips += len(result["flips"])

        total_joins += result["joins"]
        total_targets += result["target_count"]

    all_targets: list[str] = []
    all_flips: list[str] = []
    for result in results:
        all_targets.extend(result["targets"])
        if "flips" in result:
            all_flips.extend(result["flips"])

    return {
        "corner_types": corner_types,
        "is_valid": is_valid,
        "combinations": results,
        "summary": {
            "total_groups": len(results),
            "total_joins": total_joins,
            "total_targets": total_targets,
            "total_flips": total_flips,
            "buffer_count": len([b for r in results for b in r["buffers"]]),
        },
        "target_sequence": all_targets,
        "flip_sequence": all_flips,
    }


# =============================================================================
# Self-tests  (python optimizer.py)
# =============================================================================

if __name__ == "__main__":
    # ── Unit tests: rotate_corner_sticker ────────────────────────────────────
    print("=== rotate_corner_sticker tests ===")

    # UBL: CORNER_ORI["BLU"] = ["LUB", "BUL", "UBL"]  → UBL at index 2
    assert rotate_corner_sticker("UBL", 0) == "UBL", "UBL +0 should be UBL"
    assert rotate_corner_sticker("UBL", 1) == "LUB", "UBL +1 should be LUB"
    assert rotate_corner_sticker("UBL", -1) == "BUL", "UBL -1 should be BUL"

    # UFR: CORNER_ORI["FRU"] = ["RUF", "FUR", "UFR"]  → UFR at index 2
    assert rotate_corner_sticker("UFR", 0) == "UFR"
    assert rotate_corner_sticker("UFR", 1) == "RUF"
    assert rotate_corner_sticker("UFR", -1) == "FUR"

    # UBR: CORNER_ORI["BRU"] = ["RUB", "UBR", "BUR"]  → UBR at index 1
    assert rotate_corner_sticker("UBR", 0) == "UBR"
    assert rotate_corner_sticker("UBR", 1) == "BUR"
    assert rotate_corner_sticker("UBR", -1) == "RUB"

    # DFR: CORNER_ORI["DFR"] = ["RDF", "DFR", "FDR"]  → DFR at index 1
    assert rotate_corner_sticker("DFR", 0) == "DFR"
    assert rotate_corner_sticker("DFR", 1) == "FDR"
    assert rotate_corner_sticker("DFR", -1) == "RDF"

    # Non-oriented sticker starting point
    assert (
        rotate_corner_sticker("BUL", 1) == "UBL"
    )  # BUL at index 1 → +1 → index 2 → UBL
    assert rotate_corner_sticker("BUL", -1) == "LUB"  # index 1 → -1 → index 0 → LUB
    print("✓ rotate_corner_sticker OK\n")

    # ── Unit tests: type arithmetic ───────────────────────────────────────────
    print("=== Type arithmetic tests ===")

    # get_corner_type with dlin-style −1/0/+1 orientations
    assert get_corner_type({"orientation": 0, "parity": 0}) == 0
    assert get_corner_type({"orientation": 0, "parity": 1}) == 1
    assert get_corner_type({"orientation": 1, "parity": 0}) == 2
    assert get_corner_type({"orientation": 1, "parity": 1}) == 3
    assert get_corner_type({"orientation": -1, "parity": 0}) == 4  # −1 % 3 = 2
    assert get_corner_type({"orientation": -1, "parity": 1}) == 5

    # Identity: combining with type-0 is a no-op
    for t in range(NUM_CORNER_TYPES):
        assert combine_corner_types(t, 0) == t
        assert combine_corner_types(0, t) == t

    # Commutativity
    for a in range(NUM_CORNER_TYPES):
        for b in range(NUM_CORNER_TYPES):
            assert combine_corner_types(a, b) == combine_corner_types(b, a)

    # Known cancellation pairs
    assert combine_corner_types(2, 4) == 0  # CW-even  + CCW-even
    assert combine_corner_types(3, 5) == 0  # CW-odd   + CCW-odd
    assert combine_corner_types(1, 1) == 0  # correct-odd + correct-odd
    assert combine_corner_types(2, 2) == 4  # CW+CW = CCW

    # Three CCW-even cycles cancel (the parity-scramble orientation pattern)
    assert reduce(combine_corner_types, [4, 4, 4]) == 0

    print("✓ Type arithmetic OK\n")

    # ── Trace test 1: non-parity scramble (strict type-0 grouping) ───────────
    print("=== Trace test 1: non-parity scramble ===")
    # Two cycles that pair nicely: CW-even + CCW-even → type 0
    trace1 = {
        "corner": [
            # type 0 — already solved
            {
                "type": "cycle",
                "buffer": "UFR",
                "orientation": 0,
                "parity": 0,
                "targets": ["UBR", "UFL"],
            },
            # type 2 (CW, even) + type 4 (CCW, even) → combine = 0
            {
                "type": "cycle",
                "buffer": "UBL",
                "orientation": 1,
                "parity": 0,
                "targets": ["DBL", "DFL"],
            },
            {
                "type": "cycle",
                "buffer": "DFR",
                "orientation": -1,
                "parity": 0,
                "targets": ["DBR", "UBR"],
            },
        ]
    }
    standard_buf = ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"]
    r1 = analyze_corner_trace(trace1, standard_buf)
    assert r1 is not None
    assert r1["summary"]["total_groups"] == 2, (
        f"expected 2 groups, got {r1['summary']['total_groups']}"
    )
    # UFR is type-0 (solo), UBL+DFR form a strict type-0 group
    assert r1["summary"]["total_joins"] == 1
    print(
        f"  Groups:  {r1['summary']['total_groups']}  Joins: {r1['summary']['total_joins']}"
    )
    print(f"  Targets: {r1['target_sequence']}")
    print("✓ Trace test 1 OK\n")

    # ── Trace test 2: parity scramble (orientation-only fallback) ────────────
    # Matches the example in the user's message (scramble with Rw Uw).
    print("=== Trace test 2: parity scramble (orientation-only fallback) ===")
    trace2 = {
        "corner": [
            {
                "type": "misoriented",
                "buffer": "UFL",
                "orientation": -1,
                "parity": 0,
                "targets": [],
            },
            {
                "type": "cycle",
                "buffer": "UBL",
                "orientation": -1,
                "parity": 1,
                "targets": ["BDR", "FDR", "BUR"],
            },
            {
                "type": "misoriented",
                "buffer": "DFL",
                "orientation": -1,
                "parity": 0,
                "targets": [],
            },
        ]
    }
    r2 = analyze_corner_trace(trace2, standard_buf)
    assert r2 is not None, (
        "Parity-scramble trace should still pass orientation validation"
    )
    print(f"  Corner types: {r2['corner_types']}")
    print(
        f"  Groups: {r2['summary']['total_groups']}  Joins: {r2['summary']['total_joins']}"
    )
    print(f"  Targets: {r2['target_sequence']}")
    print(f"  Flips:   {r2['flip_sequence']}")
    for combo in r2["combinations"]:
        print(
            f"  Group buffers={combo['buffers']}  joins={combo['joins']}  "
            f"targets={combo['targets']}  flips={combo['flips']}"
        )
    print("✓ Trace test 2 OK\n")

    # ── Trace test 3: two correct-orientation odd-parity cycles ──────────────
    print("=== Trace test 3: two correct-orientation odd-parity cycles pair up ===")
    trace3 = {
        "corner": [
            {
                "type": "cycle",
                "buffer": "UFR",
                "orientation": 0,
                "parity": 1,
                "targets": ["UBR"],
            },
            {
                "type": "cycle",
                "buffer": "UFL",
                "orientation": 0,
                "parity": 1,
                "targets": ["DBL"],
            },
        ]
    }
    r3 = analyze_corner_trace(trace3, standard_buf)
    assert r3 is not None
    # Both are type-1 (correct-orient, odd). combine(1,1)=0 → one joined group
    assert r3["summary"]["total_groups"] == 1
    assert r3["summary"]["total_joins"] == 1
    print(
        f"  Groups: {r3['summary']['total_groups']}  Joins: {r3['summary']['total_joins']}"
    )
    print(f"  Targets: {r3['target_sequence']}")
    print("✓ Trace test 3 OK\n")

    print("=== All tests passed ===")

    # Standard buffer orders
    standard_buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]

    DEFAULTBUFFERS = {
        "corner": ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"],
        "edge": [
            "UF",
            "UB",
            "UR",
            "UL",
            "DF",
            "DB",
            "FR",
            "FL",
            "DR",
            "DL",
            "BR",
            "BL",
        ],
    }

    scrambles = ["R2 U2 B2 R F2 B2 L' B2 D2 R2 D F2 B2 U' R2 L2"]

    print("=== Enhanced Edge Cycle Optimizer - Maximizing Groups ===")
    print("Now prioritizes solutions with MORE groups (smaller group sizes)\n")

    for idx, scramble in enumerate(scrambles, start=1):
        print(f"=== Testing Scramble #{idx} ===")
        print("Scramble:", scramble)
        scramble = scramble.split()
        joined_scramble = " ".join(scramble)

        has_parity = (len(scramble) - joined_scramble.count("2")) % 2 == 1
        swap = ("UF", "UR") if has_parity else None
        print(f"{has_parity=}")
        print(f"{swap=}")
        scramble = joined_scramble

        trace = dlin.trace(scramble, trace="edges", buffers=DEFAULTBUFFERS, swap=swap)
        result = analyze_trace(trace, standard_buffer_order)

        if result:
            print(f"Edge Types: {result['edge_types']}")
            print(f"Is Valid: {result['is_valid']}")
            print(f"Summary: {result['summary']}")
        else:
            print("No result returned.")

        print("\n" + "=" * 60 + "\n")

    print("=== All tests completed ===")
