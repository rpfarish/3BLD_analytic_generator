from collections import deque
from typing import Optional

from Commutator.invert_solution import invert_solution


def _get_comm(comms, buffer, a, b) -> Optional[str]:
    try:
        return comms[buffer][a][b]
    except (KeyError, TypeError):
        return None


def comm_shift(comms, buffer, x, y, check_inverse=True) -> Optional[str]:
    if cur_comm := (
        _get_comm(comms, y, buffer, x)
        or _get_comm(comms, x, y, buffer)
        or _get_comm(comms, buffer, x, y)
    ):
        return cur_comm

    if len(buffer) == 3:
        if cur_comm := shift_corners(comms, buffer, x, y):
            return cur_comm

    if len(buffer) == 2:
        buffer = buffer[::-1]
        x = x[::-1]
        y = y[::-1]
        q = deque([buffer, x, y])

        for _ in range(3):
            q.rotate(1)
            if cur_comm := _get_comm(comms, *q):
                return cur_comm

    if check_inverse:
        return invert_solution(comm_shift(comms, y, x, buffer, check_inverse=False))

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
