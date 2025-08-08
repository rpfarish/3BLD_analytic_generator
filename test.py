import json

from Cube import Cube

with open("./settings.json") as f:
    settings = json.loads(f.read())
    letter_scheme = settings["letter_scheme"]

scramble = "Uw"
# scramble = "M' U2 M U2"
# scramble = "M2 U M2 U M' U2 M2 U2 M' U2 M2 E M2 E M2 D M2 D M' D2 M2 D2 M' D2"
scramble = "L2 F2 R2 F2 D F2 U2 R2 U F2 R2 U R' B' U' L D F2 D2 R2 R' E2 R2 E' R' U' R E R2' E2' R U"
scramble = "F2 U' R B2 L2 U2 B2 D2 B2 F D2 R2 F' D U R' D B' U' F Rw Uw2"
print(scramble)
c = Cube(scramble, ls=letter_scheme, auto_scramble=True)
# c.do_cube_rotation("y'")

# c.display_cube()

standard_buffer_order = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]

trace = c.get_dlin_trace()

print(trace)


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


get_edge_floats(trace)
