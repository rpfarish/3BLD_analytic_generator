from pprint import pprint

import dlin

from solution import Solution


def memo(scramble, letter_scheme, buffers, parity_swap_edges, buffer_order):
    if not scramble:
        return
    # todo cleanup memo output
    Solution(scramble, letter_scheme=letter_scheme, buffers=buffers, parity_swap_edges=parity_swap_edges,
             buffer_order=buffer_order).display()
    pprint(dlin.trace(scramble))
