from Cube import Memo
from Cube.drill import Drill
from Cube.letterscheme import LetterScheme, convert_letterpairs


def drill_sticker(args: list, buffers):
    """Drill: drill [-c | -e] [-r] [-f]

    Description:
        Drills a list of letterpairs from the text file until all
        pairs are drilled.

        In the text file, enter a pair as A* to drill all pairs that
        start with A (or *A for inverse).
        Letterpairs in quotes signify that a pair that was already
        drilled has occurred again.
        If frequency is not specified, it defaults to 3 and
        will reduce as cases decrease.
        Press r to repeat all of the pairs not in quotes.
        Enter q to exit anytime.
    Options:
        -c Loads corner comms to drill from drill_lists/drill_list_corners.txt
    Not Implemented:
        -e Loads edge comms to drill from drill_lists/drill_list_edges.txt
        -r Randomly generates scrambles indefinitely and does not remove drilled letterpairs
        -f Specifies the number of cycles to be included in a scramble (Recommended 2).
    Aliases:
        d
    Usage:
        drill -c
        drill -e -r -f 2
    """
    # cycles_to_exclude = None
    # if "-" not in args[0]:
    #     sticker, *args = args
    # else:
    #     sticker = None
    # if "-ex" in args:
    #     index = args.index("-ex")
    # elif "-exclude" in args:
    #     index = args.index("-exclude")
    #
    # if "-ex" in args or "-exclude" in args:
    #     cycles_to_exclude = set(args[index + 1 :])
    #     letter_scheme = LetterScheme()
    #
    #     if "-c" in args or "-corner" in args:
    #         cycles_to_exclude = {
    #             "".join(
    #                 letter_scheme.convert_pair_to_pos_type(
    #                     a.strip("\n").strip().upper(), "corner"
    #                 )
    #             )
    #             for a in cycles_to_exclude
    #         }
    #     elif "-e" in args or "-edge" in args:
    #         cycles_to_exclude = {
    #             "".join(
    #                 letter_scheme.convert_pair_to_pos_type(
    #                     a.strip("\n").strip().upper(), "edge"
    #                 )
    #             )
    #             for a in cycles_to_exclude
    #         }
    #     else:
    #
    #         if "-t" in args or "-type" in args:
    #             type_index = args.index("-t")
    #             piece_type = args[type_index + 1]
    #             piece_type = "edge" if piece_type.startswith("e") else "corner"
    #         else:
    #             piece_type = "edge" if len(sticker) == 2 else "corner"
    #
    #         cycles_to_exclude = {
    #             "".join(
    #                 letter_scheme.convert_to_pos_from_type(
    #                     a.strip("\n").strip().upper(), piece_type
    #                 )
    #             )
    #             for a in cycles_to_exclude
    #         }
    #
    # letter_scheme = LetterScheme(use_default=True)
    # # TODO::: specify some cycles you want to drill more than others
    # if "-e" in args or "-edge" in args:
    #     with open("drill_lists/drill_list_edges.txt") as f:
    #         algs = f.readlines()
    #         letter_scheme = LetterScheme()
    #         algs = {
    #             "".join(
    #                 letter_scheme.convert_pair_to_pos_type(
    #                     a.strip("\n").strip(), "edge"
    #                 )
    #             )
    #             for a in algs
    #         }
    #         Drill().drill_edge_sticker(
    #             letter_scheme=letter_scheme,
    #             sticker_to_drill=None,
    #             algs=algs,
    #             cycles_to_exclude=cycles_to_exclude,
    #             buffer=buffers["edge_buffer"],
    #         )
    #     return

    def remove_piece(target_list, piece, letter_scheme):
        piece_adj1, piece_adj2 = Memo(ls=letter_scheme).adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    def generate_drill_list(ltr_scheme: LetterScheme, buffer, target, invert=False):
        all_targets = ltr_scheme.get_corners()
        remove_piece(all_targets, buffer, letter_scheme)

        target_list = all_targets[:]
        # remove buffer stickers
        remove_piece(target_list, target, letter_scheme)

        if invert:
            return {i + target for i in target_list}

        return {target + i for i in target_list}

    freq = -1
    if "-f" in args:
        index = args.index("-f")
        freq = args[index + 1]

    letter_scheme = LetterScheme()
    all_letters = set(i.name for i in letter_scheme.scheme.values() if i.type == "c")
    all_letters.add("*")
    if "-c" in args or "-corner" in args:
        with open("drill_lists/drill_list_corners.txt") as f:
            algs = f.readlines()

            buffer = buffers["corner_buffer"]
            converted_buffer = letter_scheme[buffer]
            piece_adj1, piece_adj2 = Memo(ls=letter_scheme).adj_corners[
                converted_buffer
            ]

            # calculate the freq of each alg involving a certain piece
            new_algs = set()
            for alg in algs:
                alg = alg.strip("\n").strip().upper()

                if not alg or alg.startswith("//"):
                    continue

                if converted_buffer in alg or piece_adj1 in alg or piece_adj2 in alg:
                    print(
                        f"Please remove the buffer's letters {converted_buffer}, {piece_adj1} or {piece_adj2} from {alg}"
                    )
                    print(f"Skipping {alg}")
                    continue

                a, b = alg[: len(alg) // 2], alg[len(alg) // 2 :]
                if a not in all_letters or b not in all_letters:
                    print(
                        f"Warning: {alg} contains letters '{f"{a}" * (a not in all_letters)}{f"{b}" * (
                            b not in all_letters)}' not in the corners letterscheme"
                    )
                    print("Skipping...")
                    continue

                if "*" in alg:
                    starts_with_star = alg.startswith("*")
                    sticker_to_drill = alg[starts_with_star]

                    algs_to_drill = generate_drill_list(
                        letter_scheme,
                        converted_buffer,
                        sticker_to_drill,
                        invert=starts_with_star,
                    )

                    sticker_algs = convert_letterpairs(
                        algs_to_drill,
                        "letter_to_loc",
                        letter_scheme,
                        piece_type="corners",
                        display=False,
                        return_type="set",
                    )
                    new_algs.update(sticker_algs)
                    continue

                converted = letter_scheme.convert_pair_to_pos_type(alg, "corner")
                new_algs.add("".join(converted))

            algs = new_algs
            if not algs:
                print("Algs to drill is empty")
                return

            Drill().drill_corner_sticker(
                algs_to_drill=algs,
                letter_scheme=LetterScheme(),
                buffer=buffers["corner_buffer"],
                random_pairs="-r" in args,
                freq=freq,
            )

        return

    def remove_piece(target_list, piece, letter_scheme):
        piece_adj1 = Memo(ls=letter_scheme).adj_edges[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        return target_list

    def generate_drill_list(ltr_scheme: LetterScheme, buffer, target, invert):
        all_targets = ltr_scheme.get_edges()
        remove_piece(all_targets, buffer, ltr_scheme)

        target_list = all_targets[:]
        # remove buffer stickers
        remove_piece(target_list, target, ltr_scheme)

        # generate random pairs
        # generate specific pairs
        # generate target groups e.g. just Z or H and k
        # generate inverse target groups
        # specify buffer
        if not invert:
            return {target + i for i in target_list}
        else:
            return {i + target for i in target_list}

    letter_scheme = LetterScheme()
    all_letters = set(i.name for i in letter_scheme.scheme.values() if i.type == "e")
    all_letters.add("*")
    if "-e" in args or "-edge" in args:
        with open("drill_lists/drill_list_edges.txt") as f:
            algs = f.readlines()

            buffer = buffers["edge_buffer"]
            converted_buffer = letter_scheme[buffer]
            piece_adj1 = Memo(ls=letter_scheme).adj_edges[converted_buffer]

            # calculate the freq of each alg involving a certain piece
            new_algs = set()
            for alg in algs:
                alg = alg.strip("\n").strip().upper()

                if not alg or alg.startswith("//"):
                    continue

                if converted_buffer in alg or piece_adj1 in alg:
                    print(
                        f"Please remove the buffer's letters {converted_buffer}, {piece_adj1} "
                    )
                    print(f"Skipping {alg}")
                    continue

                a, b = alg[: len(alg) // 2], alg[len(alg) // 2 :]
                if a not in all_letters or b not in all_letters:
                    print(
                        f"Warning: {alg} contains letters '{f"{a}" * (a not in all_letters)}{f"{b}" * (
                            b not in all_letters)}' not in the edges letterscheme"
                    )
                    print("Skipping...")
                    continue

                if "*" in alg:
                    starts_with_star = alg.startswith("*")
                    sticker_to_drill = alg[starts_with_star]

                    algs_to_drill = generate_drill_list(
                        letter_scheme,
                        converted_buffer,
                        sticker_to_drill,
                        invert=starts_with_star,
                    )

                    sticker_algs = convert_letterpairs(
                        algs_to_drill,
                        "letter_to_loc",
                        letter_scheme,
                        piece_type="edges",
                        display=False,
                        return_type="set",
                    )
                    new_algs.update(sticker_algs)
                    continue

                converted = letter_scheme.convert_pair_to_pos_type(alg, "edge")
                new_algs.add("".join(converted))

            algs = new_algs
            if not algs:
                print("Algs to drill is empty")
                return

            Drill().drill_edge_sticker(
                algs_to_drill=algs,
                letter_scheme=LetterScheme(),
                buffer=buffers["edge_buffer"],
                random_pairs="-r" in args,
                freq=freq,
            )

        return
    # if "-t" in args or "-type" in args:
    #     type_index = args.index("-t")
    #     piece_type = args[type_index + 1]
    #     piece_type = "edge" if piece_type.startswith("e") else "corner"
    # else:
    #     piece_type = "edge" if len(sticker) == 2 else "corner"
    #
    # if ("-t" in args or "-type" in args) and len(sticker) == 1:
    #     scheme = LetterScheme()
    #     sticker = scheme.convert_to_pos_from_type(sticker.upper(), piece_type)
    # if ("-t" not in args or "-type" not in args) and len(sticker) == 1:
    #     print("piece type is ambiguous")
    #     return
    # if sticker in buffers.values():
    #     print("sticker must not be a buffer")
    #
    # if piece_type == "edge":
    #     # TODO::: fix so it can parse args properly
    #     cycles_to_exclude = cycles_to_exclude if cycles_to_exclude is not None else ""
    #     cycles_to_exclude = {sticker + piece for piece in cycles_to_exclude}
    #     Drill().drill_edge_sticker(
    #         letter_scheme=letter_scheme,
    #         sticker_to_drill=sticker,
    #         cycles_to_exclude=cycles_to_exclude,
    #         buffer=buffers["edge_buffer"],
    #     )
    # elif piece_type == "corner":
    #     cycles_to_exclude = cycles_to_exclude if cycles_to_exclude is not None else ""
    #     cycles_to_exclude = {sticker + piece for piece in cycles_to_exclude}
    #     Drill().drill_corner_sticker(
    #         sticker_to_drill=sticker,
    #         cycles_to_exclude=cycles_to_exclude,
    #         letter_scheme=letter_scheme,
    #         buffer=buffers["corner_buffer"],
    #     )
    # else:
    #     print("sorry not a valid piece type")
