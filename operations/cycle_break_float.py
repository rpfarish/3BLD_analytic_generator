from Cube import Drill, Cube


def cycle_break_float(buffer, buffer_order=None):
    """Syntax: cbuff <buffer>
Desc: provides scrambles with flips/twists and cycle breaks to practice all edge and corner buffers
Aliases:
    m"""
    piece_type = 'edge' if len(buffer) == 2 else 'corner'

    if piece_type == 'edge':
        cycle_break_floats_edges(buffer, buffer_order=buffer_order)
    elif piece_type == 'corner':
        cycle_break_floats_corners(buffer, buffer_order=buffer_order)


def cycle_break_floats_edges(buffer, buffer_order=None):
    """Syntax: cbuff <edge buffer>
Desc: provides scrambles with flips and cycle breaks to practice all edge buffers"""
    # todo add corners
    while True:
        drill = Drill(buffer_order=buffer_order)
        scram = drill.drill_edge_buffer_cycle_breaks(buffer)
        cube = Cube(scram, can_parity_swap=False)
        if buffer in cube.solved_edges or len(cube.flipped_edges) >= 4:
            continue
        cube_trace = cube.get_dlin_trace()
        for edge in cube_trace["edge"]:

            if (edge['type'] == "cycle" and edge["buffer"] == buffer and
                    edge['orientation'] == 0 and edge['parity'] == 0):
                cycle_breaks = False
                break
        else:
            cycle_breaks = True

        if cycle_breaks:
            print(scram)
            input()


def cycle_break_floats_corners(buffer, buffer_order=None):
    """Syntax: cbuff <corner buffer>
Desc: provides scrambles with twists and cycle breaks to practice all corner buffers"""
    while True:
        drill = Drill(buffer_order=buffer_order)
        scram = drill.drill_corner_buffer_cycle_breaks(buffer)
        cube = Cube(scram, can_parity_swap=False)
        if buffer in cube.solved_corners or len(cube.twisted_corners) > 3:
            continue
        cube_trace = cube.get_dlin_trace()
        for corner in cube_trace["corner"]:

            if (corner['type'] == "cycle" and corner["buffer"] == buffer and
                    corner['orientation'] == 0 and corner['parity'] == 0):
                cycle_breaks = False
                break
        else:
            cycle_breaks = True

        if cycle_breaks:
            print(scram)
            input()
