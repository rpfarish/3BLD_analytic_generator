from Cube.drill import Drill
from Cube.letterscheme import LetterScheme


def drill_sticker(args: list, buffers):
    """Drills a specific sticker from default buffers (UF/UFR)
(s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -ex=<cycles to exclude(secondsticker)>,
-i=<cycles to only include(secondsticker)>, -e=<edges filename>, -c=<corners filename>)

    """
    # do these two auto convert,. no.. yes
    print(args)
    letter_scheme = LetterScheme(use_default=True)

    # todo specify some cycles you want to drill more than others
    if '-e' in args:
        with open("drill_lists/drill_list_edges.txt") as f:
            algs = f.readlines()
            letter_scheme = LetterScheme(use_default=False)
            algs = {''.join(letter_scheme.convert_pair_to_pos_type(a.strip('\n').strip(), 'edge')) for a in algs}
            print(algs)
            Drill().drill_edge_sticker(
                letter_scheme=letter_scheme,
                sticker_to_drill=None,
                algs=algs
            )
    if '-c' in args:
        with open("drill_lists/drill_list_corners.txt") as f:
            algs = f.readlines()
            letter_scheme = LetterScheme(use_default=False)
            algs = {''.join(a.strip('\n').strip()) for a in algs}
            print(algs)
            Drill().drill_corner_sticker(
                sticker_to_drill=None,
                algs=algs
            )

    sticker, *args = args

    if '-t' in args:
        type_index = args.index('-t')
        piece_type = args[type_index + 1]
        piece_type = 'edge' if piece_type.startswith('e') else 'corner'
    else:
        piece_type = 'edge' if len(sticker) == 2 else 'corner'

    if '-t' in args and len(sticker) == 1:
        scheme = LetterScheme(use_default=False)
        sticker = scheme.convert_to_pos_from_type(sticker.upper(), piece_type)
    if '-t' not in args and len(sticker) == 1:
        print('piece type is ambiguous')
        return
    if sticker in buffers.values():
        print("sticker must not be a buffer")

    exclude = set()

    if piece_type == 'edge':
        # todo fix so it can parse args properly
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill().drill_edge_sticker(
            letter_scheme=letter_scheme,
            sticker_to_drill=sticker,
            return_list=False,
            cycles_to_exclude=cycles_to_exclude,
            algs=None
        )
    elif piece_type == 'corner':
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill().drill_corner_sticker(
            sticker_to_drill=sticker,
            cycles_to_exclude=cycles_to_exclude,
            algs=None
        )
    else:
        print("sorry not a valid piece type")
