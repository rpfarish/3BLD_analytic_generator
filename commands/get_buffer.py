from collections import deque
from typing import Optional

from Commutator.invert_solution import invert_solution
from Cube.letterscheme import LetterScheme
from Spreadsheets.possible_buffers import possible_buffers


def _get_comm(comms, buffer, a, b) -> Optional[str]:
    try:
        return comms[buffer][a][b]
    except (KeyError, TypeError):
        return None


def comm_shift(comms, buffer, x, y) -> Optional[str]:
    if cur_comm := (_get_comm(comms, y, buffer, x) or _get_comm(comms, x, y, buffer)):
        return cur_comm

    if len(buffer) == 3:
        return shift_corners(comms, buffer, x, y)

    if len(buffer) == 2:
        buffer = buffer[::-1]
        x = x[::-1]
        y = y[::-1]
        q = deque([buffer, x, y])

        for _ in range(3):
            q.rotate(1)
            if cur_comm := _get_comm(comms, *q):
                return cur_comm

    return None


def shift_corners(comms, buffer, x, y) -> Optional[str]:

    corner_ori = {
        "DFL": ["LDF", "FDL", "DFL"],
        "DFR": ["RDF", "DFR", "FDR"],
        "FLU": ["LUF", "UFL", "FUL"],
        "FRU": ["RUF", "FUR", "UFR"],
        "BDL": ["LDB", "DBL", "BDL"],
        "BDR": ["RDB", "BDR", "DBR"],
        "BLU": ["LUB", "BUL", "UBL"],
        "BRU": ["RUB", "UBR", "BUR"],
    }

    i, j, k = "".join(sorted(buffer)), "".join(sorted(x)), "".join(sorted(y))

    index1, index2, index3 = (
        corner_ori[i].index(buffer),
        corner_ori[j].index(x),
        corner_ori[k].index(y),
    )

    for index in range(3):
        q = deque(
            [
                corner_ori[i][(index1 + index) % 3],
                corner_ori[j][(index2 + index) % 3],
                corner_ori[k][(index3 + index) % 3],
            ]
        )
        for _ in range(3):
            q.rotate(1)
            if comm := _get_comm(comms, *q):
                return comm

    return None


def get_comm(args, file_comms, letterscheme: LetterScheme):
    # capitalization is good
    buffer, *cycles = args
    buffer = buffer.upper()

    if buffer not in possible_buffers:
        print(f"Error: '{buffer}' is not a possible buffer!")
        return None

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    max_len = max(len(name) for name, _ in file_comms)

    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = LetterScheme().convert_pair_to_pos(buffer, cycle)
        if letterscheme.is_default:
            let1, let2 = a, b
        else:
            let1, let2 = cycle

        for list_name, comms in file_comms:
            cur_comm = _get_comm(comms, buffer, a, b)
            if not cur_comm:
                cur_comm = comm_shift(comms, buffer, a, b)

            if not cur_comm:
                cur_comm = invert_solution(_get_comm(comms, buffer, b, a))
            if not cur_comm:
                cur_comm = invert_solution(comm_shift(comms, buffer, b, a))

            result = cur_comm if cur_comm else "Not listed!"
            print(f"{list_name.title():<{max_len}} {let1 + let2}: {result}")

        # I think I should create an object for lists and just pass that then
        # I wouldn't have to
        # should it show just the expanded ver or the comm notation?
        # TODO: like save both a normal comm version and an expanded version
    return buffer
