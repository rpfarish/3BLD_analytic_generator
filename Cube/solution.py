from collections import Counter
from itertools import combinations
from pprint import pprint

import dlin
from Cube.memo import Memo


class Solution:

    def __init__(
        self,
        scramble,
        letter_scheme=None,
        buffers=None,
        parity_swap_edges=None,
        buffer_order=None,
        inc_floats=True,
    ):
        self.cube = Memo(
            scramble,
            auto_scramble=False,
            can_parity_swap=True,
            ls=letter_scheme,
            buffers=buffers,
            parity_swap_edges=parity_swap_edges,
            buffer_order=buffer_order,
        )
        self.scramble = scramble
        self.parity = self.cube.has_parity
        self.cube.scramble_cube(self.scramble)

        self.edges = self.cube.format_edge_memo(self.cube.memo_edges()).split(" ")
        self.flipped_edges = list(self.cube.flipped_edges)
        self.edge_buffers = list(self.cube.edge_memo_buffers)

        self.corners = self.cube.format_corner_memo(self.cube.memo_corners()).split(" ")
        self.twisted_corners = list(self.cube.twisted_corners)
        self.corner_buffers = list(self.cube.corner_memo_buffers)
        self.can_float_corners = None

        self.number_of_edge_flips = len(self.flipped_edges) // 2
        self.number_of_corner_twists = len(self.twisted_corners) // 3
        self.number_of_algs = self.count_number_of_algs(inc_floats=inc_floats)
        self.edge_float_buffers = []
        self.can_float_edges = self.can_float_edges()
        self.inc_floats = inc_floats
        # TODO support wide moves

        # TODO return twists with top or bottom color
        # TODO add alg count

    def can_float_edges(self):
        """
        ca cb = 2e2e
        ca bc = can float
        ac bc = 2e2e
        ac cb = same as doing ab
        :return:
        """
        memo = self.edges
        buffers = self.edge_buffers
        if not self.cube.adj_edges:
            print("Edges are all solved")
            return
        print(self.cube.adj_edges)
        # flips = self.number_of_edge_flips
        # print('buffers', buffers)
        for buffer in buffers:

            is_buffer_hit = False
            buffer_hit_parity = 0
            print("memo", memo)
            for pair in memo:
                if not pair:
                    continue
                pair_len_half = len(pair) // 2
                a = pair[:pair_len_half]
                b = pair[pair_len_half:]

                # FF
                if buffer == a and not is_buffer_hit:
                    is_buffer_hit = True
                    buffer_hit_parity = 1
                    # print('2e2e or can not float', pair)
                # LL
                elif buffer == b and not is_buffer_hit:
                    is_buffer_hit = True
                    buffer_hit_parity = 2

                    # print('2e2e or with flipped edge', pair)
                # FL
                elif buffer == b and is_buffer_hit and buffer_hit_parity == 1:
                    self.edge_float_buffers.append(buffer)
                    # print('can float from buffer', buffer, pair)
                    return True

                # FL hit opp side edge
                if (
                    buffer == self.cube.adj_edges[b]
                    and is_buffer_hit
                    and buffer_hit_parity == 1
                ):
                    # print("can float from buffer, but it's flipped", buffer, pair)
                    pass

            # print("edge_buffer_count", count)
        return "maybe"

    """
    LL => ac bc = 2e2e - buffer:A <> B:C
    FL => ca bc = can float


    # INVALID STATE
    LF => ac cb = same as doing ab
    # INVALID METHOD
    FF => cb ca = 2e2e - buffer:B <> A:C

    """

    def get_float_memo(self):
        if self.can_float_edges:
            return "floating edge memo"

    def get_dlin_trace(self):
        if self.parity:
            swap = ("UF", "UR")
        else:
            swap = None

        return dlin.trace(scramble=self.scramble, swap=swap)

    def count_sandwich_floats(self):
        # TODO: switch buffers here to use settings.json
        dlin_trace = self.get_dlin_trace()
        float_count = 0
        for buffer_trace in dlin_trace["corner"] + dlin_trace["edge"]:
            can_float = (
                buffer_trace["orientation"] == 0
                and buffer_trace["parity"] == 0
                and buffer_trace["type"] == "cycle"
                and buffer_trace["buffer"] not in ["UFR", "UF"]
            )
            # todo fix this 'UFR' to self.corner_buffer etc
            if can_float:
                float_count += 1

        return float_count

    def count_number_of_algs(self, inc_floats=True) -> int:
        # TODO: do I need to tell Dlin that I'm psudo swapping UF-UR?
        number_of_floats = self.count_sandwich_floats() if inc_floats else 0

        twists_to_alg = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
        flips_to_alg = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
        # print(self.edges, len(self.edges), self.corners, len(self.corners), "FLIPS", self.number_of_edge_flips,
        #       "TWISTS", self.number_of_corner_twists, "FLOATS", number_of_floats)
        # Debug print statements for num_of_algs calculation
        print(f"DEBUG: len(self.edges) = {len(self.edges)}")
        print(f"DEBUG: len(self.corners) = {len(self.corners)}")
        print(f"DEBUG: self.number_of_edge_flips = {self.number_of_edge_flips}")
        print(
            f"DEBUG: flips_to_alg.get({self.number_of_edge_flips}, {self.number_of_edge_flips}) = {flips_to_alg.get(self.number_of_edge_flips, self.number_of_edge_flips)}"
        )
        print(f"DEBUG: self.number_of_corner_twists = {self.number_of_corner_twists}")
        print(
            f"DEBUG: twists_to_alg.get({self.number_of_corner_twists}, {self.number_of_corner_twists // 2}) = {twists_to_alg.get(self.number_of_corner_twists, self.number_of_corner_twists // 2)}"
        )

        # Calculate intermediate sum before subtracting floats
        algs_before_floats = (
            len(self.edges)
            + len(self.corners)
            + flips_to_alg.get(self.number_of_edge_flips, self.number_of_edge_flips)
            + twists_to_alg.get(
                self.number_of_corner_twists, self.number_of_corner_twists // 2
            )
        )
        print(f"DEBUG: algs_before_floats = {algs_before_floats}")
        print(f"DEBUG: number_of_floats = {number_of_floats}")

        num_of_algs = algs_before_floats - number_of_floats
        print(f"DEBUG: final num_of_algs = {num_of_algs}")
        return num_of_algs

    def get_solution(self):
        solution = {
            "scramble": self.scramble,
            "parity": self.cube.has_parity,
            "edges": self.cube.format_edge_memo(self.cube.memo_edges()).split(" "),
            "flipped_edges": list(self.cube.flipped_edges),
            "edge_buffers": list(self.cube.edge_memo_buffers),
            "can_float_edges": self.can_float_edges,
            "edge_float_buffers": self.edge_float_buffers,
            "corners": self.cube.format_corner_memo(self.cube.memo_corners()).split(
                " "
            ),
            "twisted_corners": list(self.cube.twisted_corners),
            "corner_buffers": list(self.cube.corner_memo_buffers),
            "can_float_corners": None,
            "number_of_algs": self.count_number_of_algs(inc_floats=self.inc_floats),
        }
        solution["number_of_edge_flips"] = len(solution["flipped_edges"]) // 2
        solution["number_of_corner_twists"] = len(solution["twisted_corners"]) // 3

        return solution

    def display(self):
        solution = self.get_solution()
        print("Can float edges:", self.can_float_edges)
        print("Scramble", self.scramble)
        print(f"Parity:", solution["parity"])
        print(f"Edges:", solution["edges"])
        print(f"Flipped Edges:", solution["flipped_edges"])
        print("Edge Buffers:", solution["edge_buffers"])
        print("Corners:", solution["corners"])
        print("Twisted Corners:", self.cube.twisted_corners)
        print("Alg count:", solution["number_of_algs"])
        # corner_memo = solution['corners']
        # when cube is memoed, the state of the memo should be saved when the buffer is first hit
        # no_cycle_break_corner_memo = set()
        corner_buffers = solution["corner_buffers"]
        print(corner_buffers)

        swap = ("UF", "UR") if self.parity else None
        trace = dlin.trace(self.scramble, swap=swap)
        self.get_dlin_trace_type_count_edges(trace)
        pprint(trace)

    def get_dlin_trace_type_count_edges(self, trace) -> dict[int, int]:
        edge_types = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for edge in trace["edge"]:
            # Check if type is misoriented
            if edge.get("type") == "misoriented":
                edge_types[4] += 1
                continue

            orientation = edge["orientation"]
            parity = edge["parity"]

            match (orientation, parity):
                case (0, 0):  # Type 0: normal cycle
                    edge_types[0] += 1
                case (0, 1):  # Type 1: odd cycle (needs odd cycle)
                    edge_types[1] += 1
                case (1, 0):  # Type 2: flipped cycle (needs flipped cycle)
                    edge_types[2] += 1
                case (1, 1):  # Type 3: both (needs both odd and flipped)
                    edge_types[3] += 1

        print(f"Edge types count: {edge_types}")
        # Validation checks
        sum_type_1_and_3 = edge_types[1] + edge_types[3]
        sum_type_2_3_and_4 = edge_types[2] + edge_types[3] + edge_types[4]

        print(
            f"Sum of type 1 and 3: {sum_type_1_and_3} (should be even: {sum_type_1_and_3 % 2 == 0})"
        )
        print(
            f"Sum of type 2, 3, and 4: {sum_type_2_3_and_4} (should be even: {sum_type_2_3_and_4 % 2 == 0})"
        )

        # Overall validation
        if sum_type_1_and_3 % 2 == 0 and sum_type_2_3_and_4 % 2 == 0:
            print("✓ All validation checks passed!")
        else:
            print("✗ Validation failed!")
        return edge_types


def calc_corner_alg_count() -> int:
    pass


def calc_edge_alg_count() -> int:
    # number and length of 00
    # number and length of 01
    # number and length of 11
    pass


#
# def calc_alg_count(dlin_memo):
#     # do twists and flips later
#     corner_alg_count = calc_corner_alg_count()
#     edge_alg_count = calc_edge_alg_count()
#     alg_count = corner_alg_count + edge_alg_count
#     return alg_count


def combine_types(type_a, type_b):
    """Combine two edge types using bitwise XOR on (orientation, parity)"""
    # Type mapping: 0:(0,0), 1:(0,1), 2:(1,0), 3:(1,1), 4:misoriented(1,0)
    # Note: misoriented (type 4) is treated as flipped, so same as type 2
    type_to_bits = {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1), 4: (1, 0)}
    bits_to_type = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}

    bits_a = type_to_bits[type_a]
    bits_b = type_to_bits[type_b]

    # Bitwise XOR (addition in GF(2))
    result_bits = (bits_a[0] ^ bits_b[0], bits_a[1] ^ bits_b[1])
    return bits_to_type[result_bits]


def get_edge_type(edge):
    """Get the type (0-4) of an edge based on orientation and parity"""
    if edge.get("type") == "misoriented":
        return 4

    orientation = edge["orientation"]
    parity = edge["parity"]

    if (orientation, parity) == (0, 0):
        return 0  # Type 0: normal cycle
    elif (orientation, parity) == (0, 1):
        return 1  # Type 1: odd cycle
    elif (orientation, parity) == (1, 0):
        return 2  # Type 2: flipped cycle
    elif (orientation, parity) == (1, 1):
        return 3  # Type 3: both odd and flipped


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
        # Extract buffer order from the trace data
        buffer_order = [edge["buffer"] for edge in trace["edge"]]

    # Analyze edge types first
    print("=== Edge Type Analysis ===")
    edge_types = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for edge in trace["edge"]:
        edge_type = get_edge_type(edge)
        edge_types[edge_type] += 1
        orientation = edge.get("orientation", "N/A")
        parity = edge.get("parity", "N/A")
        print(
            f"Buffer {edge['buffer']}: Type {edge_type} (orientation={orientation}, parity={parity})"
        )

    print(f"\nEdge types count: {edge_types}")

    # Validation checks
    sum_type_1_and_3 = edge_types[1] + edge_types[3]
    sum_type_2_3_and_4 = edge_types[2] + edge_types[3] + edge_types[4]
    print(
        f"Sum of type 1 and 3 (odd cycles): {sum_type_1_and_3} (should be even: {sum_type_1_and_3 % 2 == 0})"
    )
    print(
        f"Sum of type 2, 3, and 4 (flipped): {sum_type_2_3_and_4} (should be even: {sum_type_2_3_and_4 % 2 == 0})"
    )

    is_valid = sum_type_1_and_3 % 2 == 0 and sum_type_2_3_and_4 % 2 == 0
    if is_valid:
        print("✓ All validation checks passed!")
    else:
        print("✗ Validation failed!")
        return None

    # Find optimal combinations
    print("\n=== Optimal Cycle Combinations ===")
    results = find_optimal_combinations(trace["edge"], buffer_order)

    total_joins = 0
    total_targets = 0
    total_flips = 0

    for i, result in enumerate(results, 1):
        print(f"\nGroup {i}:")
        # print(f"  Primary Buffer: {result['primary_buffer']['buffer']}")
        print(f"  Buffers: {result['buffers']}")
        print(f"  Combination: {' + '.join(result['combination_path'])}")
        print(f"  Joins Required: {result['joins']}")
        print(f"  Final Type: {result['final_type']}")
        print(f"  Target Count: {result['target_count']}")
        print(f"  Targets: {result['targets']}")
        if "flips" in result and result["flips"]:
            print(f"  Flips: {result['flips']}")
            total_flips += len(result["flips"])

        total_joins += result["joins"]
        total_targets += result["target_count"]

    print(f"\n=== Summary ===")
    print(f"Total Groups: {len(results)}")
    print(f"Total Joins: {total_joins}")
    print(f"Total Targets: {total_targets}")
    print(f"Total Flips: {total_flips}")
    print(f"Buffer count: {len([b for result in results for b in result['buffers']])}")

    # List all targets in order
    print(f"\n=== All Targets in Order ===")
    all_targets = []
    all_flips = []
    for result in results:
        all_targets.extend(result["targets"])
        if "flips" in result:
            all_flips.extend(result["flips"])

    print(f"Target sequence: {all_targets}")
    if all_flips:
        print(f"Flip sequence: {all_flips}")

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

    print(f"Type 0 cycles (already solved): {[e['buffer'] for e in type_0_cycles]}")
    formatted_cycles = []
    for e in non_type_0_cycles:
        buffer = e["buffer"]
        type_ = e["type"]
        formatted_cycles.append(f"{buffer}(t{type_})")
    print("Non-type 0 cycles to combine:", formatted_cycles)

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


def find_maximum_groups(cycles, buffer_order):
    """Find maximum number of groups where each group combines to type 0 (prioritize smaller groups)"""
    from itertools import combinations

    n = len(cycles)
    if n == 0:
        return []

    # Try all possible groupings, starting with MOST groups (smallest group sizes)
    # This prioritizes solutions like [UF+FL, UB+UR] over [UF+UB+UR+FL]
    for num_groups in range(n, 0, -1):  # Count DOWN from max groups to 1
        solutions = find_groupings_with_n_groups(cycles, num_groups, buffer_order)
        if solutions:
            print(f"Found solution with {num_groups} groups (maximizing group count)")
            # Return the first valid solution
            return solutions[0]

    return []


def flip_edge_piece(piece):
    """Flip an edge piece (UB -> BU, UR -> RU, etc.)"""
    if len(piece) == 2:
        return piece[1] + piece[0]
    return piece  # Return as-is if not a 2-letter edge piece


def find_groupings_with_n_groups(cycles, num_groups, buffer_order):
    """Find all ways to partition cycles into exactly num_groups where each group sums to type 0"""
    from itertools import combinations

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
            # print("Group")
            # pprint(group)
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
            for i, cycle in enumerate(group):
                if cycle != primary_buffer:
                    buffers.append(cycle["buffer"])
                    if cycle["type"] == 4:  # misoriented - just a flip
                        flips.append(cycle["buffer"])
                    else:
                        # Add buffer to targets
                        all_targets.append(cycle["buffer"])
                        all_targets.extend(cycle["targets"])

                        return_piece = group[i]["buffer"]

                        # Check if this cycle has flipped orientation
                        if group[i]["edge"].get("orientation", 0) == 1:
                            return_piece = flip_edge_piece(return_piece)

                        all_targets.append(return_piece)

            joins_for_group = len(group) - 1  # n cycles need n-1 joins

            total_joins += joins_for_group

            formatted_groups.append(
                {
                    # "primary_buffer": primary_buffer,
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


def group_combines_to_type_0(group):
    """Check if a group of cycles combines to type 0"""
    if not group:
        return False

    current_type = group[0]["type"]
    for cycle in group[1:]:
        current_type = combine_types(current_type, cycle["type"])

    return current_type == 0


# Standard buffer order for edges
standard_buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]

DEFAULTBUFFERS = {
    "corner": ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"],
    "edge": ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL", "BR", "BL"],
}


# List of scrambles to test
scrambles = [
    "F2 U' R B2 L2 U2 B2 D2 B2 F D2 R2 F' D U R' D B' U' F Rw Uw2",
    "L2 F2 R2 F2 D F2 U2 R2 U F2 R2 U R' B' U' L D F2 D2 R2 R' E2 R2 E' R' U' R E R2' E2' R U",
    "F' U2 R2 U2 B' D2 F' L2 U2 L2 R' U' L U2 B' D F U2 R U' Rw",
    "D' L' U2 B2 U F2 D L2 U B2 D2 F2 D' L' F' R2 B2 U' F' L2 Uw",
    "D B' D2 R2 B F R2 F2 R2 U2 F U' B' D B R' U2 B' F' Fw Uw'",
    "D U2 R2 D2 R2 F2 D2 F' L2 B2 F R2 D F' U' L2 F' L' D' L' Fw' Uw",
    "R' B D R2 B' R B' F2 D' R2 F2 R2 D F2 U' F2 B2 R' D Fw Uw",
    "B U2 F2 L' D F' D2 R U2 R2 U2 B2 U B2 U L2 D' R2 B2 L Fw'",
    "D R' L2 D' L2 U B2 R2 D2 F2 R2 D2 F D R' B U F U2 F2 Fw Uw",
    "B F2 U2 L D2 L2 D2 L2 U2 B2 L U2 D L D' U2 R2 F' U' Uw'",
    "B2 D2 L2 R2 B' U2 F' R2 U2 B2 U2 F D' R' U' F R' B2 F R' B' Rw Uw2",
    "R F' U F2 R2 U' B D' U2 L' F2 L D2 R' U2 F2 B2 R2 D2 Fw Uw",
    "F2 D' F' B L' B D' F2 R' F B D2 F R2 F U2 F2 D2 R2 U2 R2 Rw Uw2",
    "D R' L2 B D2 B D2 U2 B2 L2 B U2 R2 F2 R B D F2 D L2 U Rw Uw'",
    "D' F2 L2 U' R2 F2 L2 B2 D L2 U2 F2 R D' R2 B2 F U F2 R' F' Fw Uw'",
    "R2 F' U2 D' F' R2 L2 F L F' R2 D2 B R2 U2 L2 F' L2 D2 B' Rw",
    "L2 B2 D2 F2 D' U2 L2 F2 L2 F D2 L U' F' R U' F2 L' D' Fw",
    "B2 U B2 R2 F2 U2 R2 F2 D R2 B2 D F D L R' B' D B' F U' Fw Uw'",
    "R2 D2 B2 L' F2 L R2 B2 R2 F2 U2 R' F' U B2 U R' B2 L' D' F' Rw Uw",
    "F2 R D2 U2 B2 R D2 R B2 L' D R U2 F U2 F' D' Rw2 Uw'",
    "L' F' D' F2 L U2 D' R F2 L B2 U2 R2 L' F2 L U2 B' Rw2 Uw'",
    "F R F2 R2 U L D' R F2 L D2 R2 F2 L2 F2 U2 L F U2 Rw2 Uw2",
    "L' F L F L' B R' B2 R2 U2 F2 R' D2 F2 L' F2 R' U2 Rw' Uw2",
    "F L F2 U2 R' U2 R' B2 U2 B2 L F R2 D L B' D' U B2 R Uw",
    "F' B' R U' D2 B2 U F' R F2 U2 D2 B' D2 F2 U2 L2 U2 F U2 L2 Rw Uw'",
    "R B' D F2 U2 L2 F2 D R2 D' R2 F2 L2 U2 F' L2 U R' U' B' U' Rw2 Uw",
    "L2 U2 R' B2 F2 D2 R U2 L U2 B2 R2 D R' U2 B2 F' D' F' R2 F2 Uw",
    "L2 R2 U' F2 D' R2 D' B2 U B2 U' B2 L D L U2 F' U' R2 B2 R2 Rw2 Uw'",
    "R' B' R' B2 L2 F2 L' U2 R2 D2 R F2 U2 D' F' D' B' F' L' D Rw Uw'",
    "L B2 R2 F' U2 L2 B' D2 F' R2 B2 U2 L' D' L2 B2 L D' U' F' Fw' Uw2",
    "R' F2 R2 F U2 B2 U2 L2 D2 F' U2 F D B2 D' R' U B2 L' U Rw2",
    "L' F2 L' U2 L' B2 U2 L' F2 U2 R' F2 D' R B' D2 F' U' R2 B2 L2 Fw' Uw'",
    "L2 U' R2 U' R2 U2 B2 F2 L2 U R2 B F' L F R2 F' U2 R2 F U' Rw' Uw'",
    "R' D' B2 R2 F U2 R2 B' D2 F' U2 F R2 L' U2 B D' U' R' D' Rw' Uw2",
]

# scrambles = ["L2 R2 U' F2 D' R2 D' B2 U B2 U' B2 L D L U2 F' U' R2 B2 R2 Rw2 Uw'"]
print("=== Enhanced Edge Cycle Optimizer - Maximizing Groups ===")
print("Now prioritizes solutions with MORE groups (smaller group sizes)\n")

# Loop through all scrambles
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
    trace = dlin.trace(scramble, buffers=DEFAULTBUFFERS, swap=swap)
    result = analyze_trace(trace, standard_buffer_order)

    if result:
        print(f"Edge Types: {result['edge_types']}")
        print(f"Is Valid: {result['is_valid']}")
        print(f"Summary: {result['summary']}")
    else:
        print("No result returned.")

    print("\n" + "=" * 60 + "\n")

print("=== All tests completed ===")
if __name__ == "__main__":
    # R U' D2 F2 L' B D R2 F B2 L2 U R2 B2 D2 F2 D' L2 D2 R2 F2 L B'
    s = Solution("D F' D2 L2 R' D2 F2 R' L F B R L' F' D U2 B F2 U' R")
    print(s.count_number_of_algs())
