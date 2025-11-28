from Cube import Drill


def drill_cycle_break(args, buffers):

    sticker_to_drill = args[0]
    corner_buffer = buffers["corner_buffer"]
    edge_buffer = buffers["edge_buffer"]
    if len(sticker_to_drill) == 1:
        print("Please enter sticker type as UFL or UR")
    piece_type = "c" if len(sticker_to_drill) == 3 else "e"

    if piece_type == "c":
        Drill().drill_cycle_break_corners(corner_buffer, sticker_to_drill)

        pass
        # drill cycle break corners

    if piece_type == "e":
        print("Not Implemented yet")
        pass
        # drill cycle break edges
