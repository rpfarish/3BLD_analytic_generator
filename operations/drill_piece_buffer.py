from Cube.drill import Drill


def drill_piece_buffer(piece_type: str, buffer: str, drill_list: set | None, random_pairs: bool, buffer_order=None,
                       file_comms=None):
    # todo somehow combine these two!?!
    if piece_type == 'e':
        Drill(buffer_order=buffer_order).drill_edge_buffer(edge_buffer=buffer, translate_memo=True,
                                                           drill_set=drill_list,
                                                           random_pairs=random_pairs, file_comms=file_comms)
    if piece_type == 'c':
        Drill(buffer_order=buffer_order).drill_corner_buffer(corner_buffer=buffer, drill_set=drill_list,
                                                             random_pairs=random_pairs, file_comms=file_comms)
