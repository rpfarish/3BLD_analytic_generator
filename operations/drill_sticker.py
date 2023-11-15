from Cube.drill import Drill


def drill_sticker(sticker, exclude=None, buffer_order=None):
    """Drills a specific sticker from default buffers (UF/UFR)"""
    # todo specify some cycles you want to drill more than others

    piece_type = 'edge' if len(sticker) == 2 else 'corner'

    if exclude is None:
        exclude = set()

    if piece_type == 'edge':
        # todo fix so it can parse args properly
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill(buffer_order=buffer_order).drill_edge_sticker(
            sticker_to_drill=sticker, return_list=False, cycles_to_exclude=cycles_to_exclude,
        )
    elif piece_type == 'corner':
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill(buffer_order=buffer_order).drill_corner_sticker(sticker_to_drill=sticker)
    else:
        print("sorry not a valid piece type")
