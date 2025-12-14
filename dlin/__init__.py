from typing import TypedDict

from dlin.tracer import Tracer


class DefaultBuffers(TypedDict):
    corner: list[str]
    edge: list[str]


DEFAULTBUFFERS: DefaultBuffers = {
    "corner": ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL", "DBR", "DBL"],
    "edge": ["UF", "UB", "UR", "UL", "FR", "FL", "DF", "DB", "DR", "DL", "BR", "BL"],
}


def trace(scramble, buffers=DEFAULTBUFFERS, trace="both", swap=None):
    s = Tracer(buffers, trace)
    if swap:
        e1, e2 = swap
        s.manual_swap(e1, e2)
    s.scramble_from_string(scramble)
    s.trace_cube()
    return s.tracing
