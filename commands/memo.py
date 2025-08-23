from Cube.solution import Solution


def memo(scramble, letter_scheme, buffers, parity_swap_edges, buffer_order):
    if not scramble:
        return
    # todo cleanup memo output
    s = Solution(
        scramble,
        letter_scheme=letter_scheme,
        buffers=buffers,
        parity_swap_edges=parity_swap_edges,
        buffer_order=buffer_order,
    )
    s.display()
