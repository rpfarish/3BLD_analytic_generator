import json
from pprint import pprint

import dlin

import get_scrambles
from Cube import Cube
from Cube.drill import Drill
from Cube.letterscheme import LetterScheme
from operations.get_buffer import get_comm
from solution import Solution


def memo(scramble, letter_scheme, buffers, parity_swap_edges, buffer_order):
    if not scramble:
        return
    # todo cleanup memo output
    Solution(scramble, letter_scheme=letter_scheme, buffers=buffers, parity_swap_edges=parity_swap_edges,
             buffer_order=buffer_order).display()
    pprint(dlin.trace(scramble))


def memo_cube(scramble, letter_scheme, buffers, parity_swap_edges, buffer_order):
    """Memo: memo [scramble] [-l filename] [-s filename]
Options:
    -l filename loads scrambles from FILENAME text file
    -s filename saves SCRAMBLE to FILENAME text file
Aliases:
    m
    """

    scramble = " ".join(scramble)

    if scramble.startswith('-l'):
        _, file_name = scramble.split()
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        with open(file_name) as f:
            for num, scram in enumerate(f.readlines(), 1):
                # print("Scramble number:", num)
                memo(scram.strip("\n").strip().strip('"'), letter_scheme, buffers, parity_swap_edges, buffer_order)
        return

    elif '-s' in scramble:
        scramble = scramble.strip('"').split()
        f_index = scramble.index('-s')
        file_name = scramble[f_index + 1]
        scramble = scramble[:f_index]
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        scramble = " ".join(scramble)

        with open(file_name, 'a+') as f:
            f.write(scramble.strip('"'))
            f.write("\n")
            f.close()

    memo(scramble.strip('"'), letter_scheme, buffers, parity_swap_edges, buffer_order=buffer_order)


def set_letter_scheme(args, letter_scheme: LetterScheme) -> LetterScheme:
    """Letter Scheme: ls [-d] [-l] [-c]
Options:
    -d dumps the current loaded letter scheme for the standard Singmaster notation
    -l loads the letter scheme from settings.json
    -c prints the current letter scheme
Aliases:
    letterscheme"""
    # todo add current
    if '-cur' in args or '-c' in args:
        print("Current:", letter_scheme.get_all_dict())
        return letter_scheme
    elif '-dump' in args or '-d' in args:
        print("Previous:", letter_scheme.get_all_dict())
        print("Current: ", LetterScheme(use_default=True).get_all_dict())
        return LetterScheme(use_default=True)
    elif '-load' in args or '-l' in args:
        print("Previous:", letter_scheme.get_all_dict())
        with open("settings.json") as f:
            settings = json.loads(f.read())
            print("Current: ", LetterScheme(ltr_scheme=settings['letter_scheme']).get_all_dict())
            return LetterScheme(ltr_scheme=settings['letter_scheme'])
    else:
        print("Warning action not performed")
        print("Reloading letterscheme")
        return set_letter_scheme(["-load"], letter_scheme)


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


def drill_buffer(args, filename, buffer, buffer_order, file_comms):
    drill_set = None
    random_pairs = False
    if '-r' in args:
        random_pairs = True
    elif '-l' not in args:
        with open(f"{filename}", "r+") as f:
            drill_list = json.load(f)
            buffer_drill_list = drill_list.get(buffer, [])
            if len(buffer_drill_list) > 0:
                print("Buffer drill file is not empty for that buffer")
                print(len(buffer_drill_list), "comms remaining")
                print("Continuing will result the rewriting of the buffer drill file")
                response = input("Are you sure you want to continue y/n?: ").lower()
                if response not in ['y', 'yes']:
                    print("Aborting...")
                    return

    elif '-l' in args:
        if len(args) > 1:
            filename = args.find('-l') + 1

        # load file
        print("Loading drill_save.json")
        with open(f"{filename}", "r+") as f:
            drill_list = json.load(f)
            buffer_drill_list = drill_list.get(buffer)
            if buffer_drill_list is None or not buffer_drill_list:
                print("Savefile empty for that buffer")
                print(f"Adding {buffer} to savefile")
                drill_list[buffer] = []
                f.close()
        with open(f"{filename}", "w") as f:
            json.dump(drill_list, f, indent=4)
            f.close()
        drill_set = set(drill_list[buffer])
    else:
        drill_set = None

    # to load 1. Buffer 2. Remaining cycles
    piece_type = 'c' if len(buffer) == 3 else 'e'
    drill_piece_buffer(piece_type, buffer.upper(), drill_list=drill_set, random_pairs=random_pairs,
                       buffer_order=buffer_order, file_comms=file_comms)


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


def alger(alg_count, buffer_order):
    # todo check this
    """Syntax: alger <alg count>
Desc: generates a scramble with specified number of algs
Note: recommended alg range is 7-13 (still needs checking)"""
    while True:
        scramble = ""
        cur_alg_count = 0
        while cur_alg_count != alg_count:
            scramble = get_scrambles.get_scramble()
            cur_alg_count = Solution(scramble=scramble, buffer_order=buffer_order).count_number_of_algs()

        print(scramble)
        input()


# todo letterscheme
# todo change which lists are displayed when the buffer is drilled

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


def get_comm_loop(args, file_comms, comm_file_name, letter_scheme: LetterScheme):
    rapid_mode = False
    if '-r' in args:
        rapid_mode = True
        args.remove('-r')

    buffer = get_comm(args, file_comms, comm_file_name, letterscheme=letter_scheme)

    while rapid_mode:
        args = input("(rapid) ").split()
        if 'quit' in args or 'exit' in args:
            break

        if '-b' in args:
            buffer = args[args.index('-b') + 1]
            args.remove('-b')
        else:
            args = [buffer] + args

        get_comm(args, file_comms, comm_file_name, letterscheme=letter_scheme)
