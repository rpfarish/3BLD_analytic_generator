from Cube.drill import Drill
from Cube.letterscheme import LetterScheme


def drill_sticker(args: list, buffers):
    """Drills a specific sticker from default buffers (UF/UFR)
    (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional
    -i=<cycles to only include(secondsticker)>, -e=<edges filename>, -c=<corners filename>,
    -ex=<cycles to exclude(secondsticker)(must be last)>)
    """
    cycles_to_exclude = None
    if "-" not in args[0]:
        sticker, *args = args
    else:
        sticker = None
    if "-ex" in args:
        index = args.index("-ex")
    elif "-exclude" in args:
        index = args.index("-exclude")

    if "-ex" in args or "-exclude" in args:
        cycles_to_exclude = set(args[index + 1 :])
        letter_scheme = LetterScheme()

        if "-c" in args or "-corner" in args:
            cycles_to_exclude = {
                "".join(
                    letter_scheme.convert_pair_to_pos_type(
                        a.strip("\n").strip().upper(), "corner"
                    )
                )
                for a in cycles_to_exclude
            }
        elif "-e" in args or "-edge" in args:
            cycles_to_exclude = {
                "".join(
                    letter_scheme.convert_pair_to_pos_type(
                        a.strip("\n").strip().upper(), "edge"
                    )
                )
                for a in cycles_to_exclude
            }
        else:

            if "-t" in args or "-type" in args:
                type_index = args.index("-t")
                piece_type = args[type_index + 1]
                piece_type = "edge" if piece_type.startswith("e") else "corner"
            else:
                piece_type = "edge" if len(sticker) == 2 else "corner"

            cycles_to_exclude = {
                "".join(
                    letter_scheme.convert_to_pos_from_type(
                        a.strip("\n").strip().upper(), piece_type
                    )
                )
                for a in cycles_to_exclude
            }

    letter_scheme = LetterScheme(use_default=True)
    # todo specify some cycles you want to drill more than others
    if "-e" in args or "-edge" in args:
        with open("drill_lists/drill_list_edges.txt") as f:
            algs = f.readlines()
            letter_scheme = LetterScheme()
            algs = {
                "".join(
                    letter_scheme.convert_pair_to_pos_type(
                        a.strip("\n").strip(), "edge"
                    )
                )
                for a in algs
            }
            Drill().drill_edge_sticker(
                letter_scheme=letter_scheme,
                sticker_to_drill=None,
                algs=algs,
                cycles_to_exclude=cycles_to_exclude,
                buffer=buffers["edge_buffer"],
            )
        return
    if "-c" in args or "-corner" in args:
        with open("drill_lists/drill_list_corners.txt") as f:
            algs = f.readlines()
            letter_scheme = LetterScheme()
            algs = {
                "".join(
                    letter_scheme.convert_pair_to_pos_type(
                        a.strip("\n").strip(), "corner"
                    )
                )
                for a in algs
            }
            Drill().drill_corner_sticker(
                sticker_to_drill=None,
                algs=algs,
                cycles_to_exclude=cycles_to_exclude,
                buffer=buffers["corner_buffer"],
            )
        return

    if "-t" in args or "-type" in args:
        type_index = args.index("-t")
        piece_type = args[type_index + 1]
        piece_type = "edge" if piece_type.startswith("e") else "corner"
    else:
        piece_type = "edge" if len(sticker) == 2 else "corner"

    if ("-t" in args or "-type" in args) and len(sticker) == 1:
        scheme = LetterScheme()
        sticker = scheme.convert_to_pos_from_type(sticker.upper(), piece_type)
    if ("-t" not in args or "-type" not in args) and len(sticker) == 1:
        print("piece type is ambiguous")
        return
    if sticker in buffers.values():
        print("sticker must not be a buffer")

    if piece_type == "edge":
        # todo fix so it can parse args properly
        cycles_to_exclude = cycles_to_exclude if cycles_to_exclude is not None else ""
        cycles_to_exclude = {sticker + piece for piece in cycles_to_exclude}
        Drill().drill_edge_sticker(
            letter_scheme=letter_scheme,
            sticker_to_drill=sticker,
            cycles_to_exclude=cycles_to_exclude,
            buffer=buffers["edge_buffer"],
        )
    elif piece_type == "corner":
        cycles_to_exclude = cycles_to_exclude if cycles_to_exclude is not None else ""
        cycles_to_exclude = {sticker + piece for piece in cycles_to_exclude}
        Drill().drill_corner_sticker(
            sticker_to_drill=sticker,
            cycles_to_exclude=cycles_to_exclude,
            letter_scheme=letter_scheme,
            buffer=buffers["corner_buffer"],
        )
    else:
        print("sorry not a valid piece type")
