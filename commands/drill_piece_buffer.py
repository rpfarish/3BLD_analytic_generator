from Cube.drill import Drill


def drill_piece_buffer(
    file_comms,
    piece_type: str,
    buffer: str,
    drill_list: set | None,
    random_pairs: bool,
    buffer_order=None,
    letter_scheme=None,
    return_list=False,
    number_of_scrambles=0,
):
    # TODO:: somehow combine these two!?!
    if piece_type == "e":
        Drill(buffer_order=buffer_order).drill_edge_buffer(
            file_comms,
            edge_buffer=buffer,
            return_list=return_list,
            translate_memo=True,
            drill_set=drill_list,
            random_pairs=random_pairs,
            number_of_scrambles=number_of_scrambles,
        )
    if piece_type == "c":
        Drill(buffer_order=buffer_order).drill_corner_buffer(
            corner_buffer=buffer,
            drill_set=drill_list,
            return_list=return_list,
            random_pairs=random_pairs,
            file_comms=file_comms,
            number_of_scrambles=number_of_scrambles,
        )
