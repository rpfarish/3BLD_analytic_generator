import json
from pprint import pprint

import dlin
from Cube import Cube
from Cube.dlin_float import find_optimal_combinations

with open("./settings.json") as f:
    settings = json.loads(f.read())
    letter_scheme = settings["letter_scheme"]

scramble = "Uw"
# scramble = "M' U2 M U2"
# scramble = "M2 U M2 U M' U2 M2 U2 M' U2 M2 E M2 E M2 D M2 D M' D2 M2 D2 M' D2"
scramble = "L2 F2 R2 F2 D F2 U2 R2 U F2 R2 U R' B' U' L D F2 D2 R2 R' E2 R2 E' R' U' R E R2' E2' R U"
scramble = "F2 U' R B2 L2 U2 B2 D2 B2 F D2 R2 F' D U R' D B' U' F Rw Uw2"
scramble = "D R' L2 D' L2 U B2 R2 D2 F2 R2 D2 F D R' B U F U2 F2 Fw Uw"
print(scramble)
c = Cube(scramble, ls=letter_scheme, auto_scramble=True)
# c.do_cube_rotation("y'")

# c.display_cube()

standard_buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]

trace = c.get_dlin_trace()

# print(trace)


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


def get_type_0_buffers(trace) -> list[str]:
    return [edge["buffer"] for edge in trace["edge"] if get_edge_type(edge) == 0]


def get_edge_floats(trace):
    buffer_order = []

    dlin_buffers = [edge["buffer"] for edge in trace["edge"]]
    for buffer in standard_buffer_order:
        if buffer in dlin_buffers:
            buffer_order.append(buffer)

    if not buffer_order:
        return

    print(f"{buffer_order=}")
    type_0_buffers = get_type_0_buffers(trace)
    print("Type 0 buffers:", type_0_buffers)
    remaining_buffers = [
        buffer for buffer in dlin_buffers if buffer not in type_0_buffers
    ]

    edge_data = []

    for edge in remaining_buffers:
        pass

    def backtrack(trace, buffers, solutions):
        pass


# get_edge_floats(trace)


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
    "F2 R2 U2 R2 U' B2 L2 U B2 D L2 F' L' B' U2 F' U R' D' U' R F",
    "B2 U' B2 R2 D2 L2 U B2 D B2 D' L' B2 R' B R2 L D' U2 B' U R",
    "D R' L2 D' L2 U B2 R2 D2 F2 R2 D2 F D R' B U F U2 F2 Fw Uw",
]
scrambles = [
    "U F L' B2 R2 U R D F' D2 F' U2 F' U2 L2 F2 R2 D2 B2 U' Rw2 Uw'",
    "D2 B' U' L' D2 R B2 U2 B2 R U2 L' R' U2 F D' U2 L2 R D L Fw' Uw2",
    "U2 L B U2 R2 D' L R2 D2 B L2 B L2 B U2 F D2 B L' F' Rw' Uw",
    "R F2 U2 L2 D2 F D2 L2 F' U2 R2 F' D B' L2 R D R2 F2 R2 U Rw Uw",
    "U F2 U L2 U' R2 U' F2 L2 U2 B2 U L' R U' L F2 R2 B' R' F2 Rw2 Uw",
    "L2 R2 D2 B2 F' R2 F2 U2 B' U2 R2 D2 L' U B2 L' U B D' R U Uw",
    "F' L2 F' L2 R2 F2 U2 B' D2 L2 B2 U2 R' U L2 F2 R' D2 U R F' Fw Uw2",
    "R2 B F2 D' F2 R2 D' U2 R2 D2 F2 D' B2 L' B F' L U L2 U' R Uw",
    "D2 R B U L' U R' F' D' B2 R D2 L2 B2 R U2 L F2 U2 L2 Fw' Uw2",
    "F2 R B2 U R' U2 R F U2 F D2 F2 U2 F' R2 F2 D2 F' L2 D R Rw Uw'",
    "B' L2 R2 B U2 F R2 B' L2 F' R U' R2 B' F2 R' U F' R' F Uw'",
    "D B U2 B' L2 D2 F D2 L2 R2 B L2 F' R' F2 R' B R2 F' D' Uw'",
    "D' F' U2 B2 R2 D' B2 U2 R2 U' R2 D' R2 U' F' U F2 L' R2 D' F Uw2",
    "U' B U2 L B L2 D B2 R F R2 U2 F2 B' L2 F U2 F' D2 F' Rw2 Uw",
    "R2 F2 L2 U' R2 D' R2 D2 B2 F2 L2 B R U2 R' F2 U' F U R' Rw Uw2",
    "U2 F2 D R2 U2 F2 U L2 U R2 B D' F2 R U2 L2 U' L B' F' Fw",
    "R' U2 L2 B2 D' B2 U' F2 U' B2 D L2 U' B R B' R2 D2 F' D B Rw' Uw",
    "U2 F2 D2 F2 U' L2 F2 D' F2 U' B' L U' L2 B2 F2 R' U L F' Rw Uw",
    "B' R2 F D2 F' L2 B' U2 R2 B R2 U B' D U B2 L B D' U Fw Uw2",
    "L2 R2 U' L2 D' F2 D2 R2 U R2 L U2 F' U' R B U L U' R' Fw",
    "R2 B2 U2 L B2 D2 F2 L D2 R F2 R2 U L' B U' B2 F D' R U' Fw' Uw2",
]

# scrambles = ["L2 R2 U' F2 D' R2 D' B2 U B2 U' B2 L D L U2 F' U' R2 B2 R2 Rw2 Uw'"]
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

    buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]
    results = find_optimal_combinations(trace["edge"], buffer_order)
    pprint(results)
    # result = analyze_trace(trace, standard_buffer_order)

    # if result:
    #     print(f"Edge Types: {result['edge_types']}")
    #     print(f"Is Valid: {result['is_valid']}")
    #     print(f"Summary: {result['summary']}")
    # else:
    #     print("No result returned.")
    #
    print("\n" + "=" * 60 + "\n")

print("=== All tests completed ===")
