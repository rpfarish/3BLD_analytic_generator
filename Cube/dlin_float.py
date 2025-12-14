from functools import reduce
from itertools import combinations

import dlin


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
    # print("=== Edge Type Analysis ===")
    edge_types = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for edge in trace["edge"]:
        edge_type = get_edge_type(edge)
        edge_types[edge_type] += 1
        # orientation = edge.get("orientation", "N/A")
        # parity = edge.get("parity", "N/A")
        # print(
        #     f"Buffer {edge['buffer']}: Type {edge_type} (orientation={orientation}, parity={parity})"
        # )

    # print(f"\nEdge types count: {edge_types}")

    # Validation checks
    sum_type_1_and_3 = edge_types[1] + edge_types[3]
    sum_type_2_3_and_4 = edge_types[2] + edge_types[3] + edge_types[4]
    # print(
    #     f"Sum of type 1 and 3 (odd cycles): {sum_type_1_and_3} (should be even: {sum_type_1_and_3 % 2 == 0})"
    # )
    # print(
    #     f"Sum of type 2, 3, and 4 (flipped): {sum_type_2_3_and_4} (should be even: {sum_type_2_3_and_4 % 2 == 0})"
    # )

    is_valid = sum_type_1_and_3 % 2 == 0 and sum_type_2_3_and_4 % 2 == 0
    if is_valid:
        print("✓ All validation checks passed!")
    else:
        print("✗ Validation failed!")
        return None

    # Find optimal combinations
    # print("\n=== Optimal Cycle Combinations ===")
    results = find_optimal_combinations(trace["edge"], buffer_order)

    total_joins = 0
    total_targets = 0
    total_flips = 0

    for i, result in enumerate(results, 1):
        # print(f"\nGroup {i}:")
        # # print(f"  Primary Buffer: {result['primary_buffer']['buffer']}")
        # print(f"  Buffers: {result['buffers']}")
        # print(f"  Combination: {' + '.join(result['combination_path'])}")
        # print(f"  Joins Required: {result['joins']}")
        # print(f"  Final Type: {result['final_type']}")
        # print(f"  Target Count: {result['target_count']}")
        # print(f"  Targets: {result['targets']}")
        if "flips" in result and result["flips"]:
            # print(f"  Flips: {result['flips']}")
            total_flips += len(result["flips"])

        total_joins += result["joins"]
        total_targets += result["target_count"]

    # print(f"\n=== Summary ===")
    # print(f"Total Groups: {len(results)}")
    # print(f"Total Joins: {total_joins}")
    # print(f"Total Targets: {total_targets}")
    # print(f"Total Flips: {total_flips}")
    # print(f"Buffer count: {len([b for result in results for b in result['buffers']])}")

    # List all targets in order
    # print(f"\n=== All Targets in Order ===")
    all_targets = []
    all_flips = []
    for result in results:
        all_targets.extend(result["targets"])
        if "flips" in result:
            all_flips.extend(result["flips"])

    # print(f"Target sequence: {all_targets}")
    # if all_flips:
    #     print(f"Flip sequence: {all_flips}")

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

    # print(f"Type 0 cycles (already solved): {[e['buffer'] for e in type_0_cycles]}")
    formatted_cycles = []
    for e in non_type_0_cycles:
        buffer = e["buffer"]
        type_ = e["type"]
        formatted_cycles.append(f"{buffer}(t{type_})")
    # print("Non-type 0 cycles to combine:", formatted_cycles)

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
            # print(f"Found solution with {num_groups} groups (maximizing group count)")
            # Return the first valid solution
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


def group_combines_to_type_0(group) -> bool:
    """Check if a group of cycles combines to type 0"""
    if not group:
        return False

    types = [cycle["type"] for cycle in group]
    current_type = reduce(combine_types, types)

    return current_type == 0


if __name__ == "__main__":
    # Standard buffer order for edges
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
    scrambles = ["R2 U2 B2 R F2 B2 L' B2 D2 R2 D F2 B2 U' R2 L2"]

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
        # TODO: put this in a test module or something
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
