import json
import time
from pprint import pprint
from typing import List, Tuple

import dlin

import drill_generator
import get_scrambles
from Cube import Cube
from Cube.drill import Drill
from Cube.letterscheme import LetterScheme
from convert_list_to_comms import update_comm_list
from eli_comms import ELI_COMMS
from max_comms import MAX_COMMS
from solution import Solution


# todo settings with buffer order and alt pseudo swaps for each parity alg
# todo how to ingest a new comm sheet esp full floating

def memo(scramble, letter_scheme):
    if not scramble:
        return
    # todo cleanup memo output
    Solution(scramble, letter_scheme=letter_scheme).display()
    pprint(dlin.trace(scramble))


def memo_cube(scramble, letter_scheme):
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
                print("Scramble number:", num)
                pprint(memo(scram.strip("\n").strip().strip('"'), letter_scheme))

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

    memo(scramble.strip('"'), letter_scheme)


def set_letter_scheme(args, letter_scheme) -> LetterScheme:
    """Letter Scheme: ls [-d] [-l]
Options:
    -d dumps the current loaded letter scheme for the standard Singmaster notation
    -l loads the letter scheme from settings.json
Aliases:
    letterscheme"""
    if '-dump' in args or '-d' in args:
        pprint(letter_scheme.get_all_dict(), sort_dicts=False)
        return LetterScheme(use_default=True)
    if '-load' in args or '-l' in args:
        with open("settings.json") as f:
            settings = json.loads(f.read())
            pprint(letter_scheme.get_all_dict(), sort_dicts=False)
            return LetterScheme(ltr_scheme=settings['letter_scheme'])


def drill_sticker(sticker, exclude=None):
    """Drills a specific sticker from default buffers (UF/UFR)"""
    # todo specify some cycles you want to drill more than others

    piece_type = 'edge' if len(sticker) == 2 else 'corner'

    if exclude is None:
        exclude = set()

    if piece_type == 'edge':
        # todo fix so it can parse args properly
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill().drill_edge_sticker(
            sticker_to_drill=sticker, return_list=False, cycles_to_exclude=cycles_to_exclude
        )
    elif piece_type == 'corner':
        cycles_to_exclude = {sticker + piece for piece in exclude}
        Drill().drill_corner_sticker(sticker_to_drill=sticker)
    else:
        print("sorry not a valid piece type")


def drill_buffer(piece_type: str, buffer: str, drill_list: set | None, random_pairs: bool):
    # todo somehow combine these two!?!
    if piece_type == 'e':
        Drill().drill_edge_buffer(edge_buffer=buffer, translate_memo=True, drill_set=drill_list,
                                  random_pairs=random_pairs)
    if piece_type == 'c':
        Drill().drill_corner_buffer(corner_buffer=buffer, drill_set=drill_list, random_pairs=random_pairs)


def alger(alg_count):
    # todo check this
    """Syntax: alger <alg count>
Desc: generates a scramble with specified number of algs
Note: recommended alg range is 7-13 (still needs checking)"""
    while True:
        scramble = ""
        cur_alg_count = 0
        while cur_alg_count != alg_count:
            scramble = get_scrambles.get_scramble()
            cur_alg_count = Solution(scramble=scramble).count_number_of_algs()

        print(scramble)
        input()


# todo letterscheme
# todo change which lists are displayed when the buffer is drilled

def cycle_break_float(buffer):
    """Syntax: cbuff <buffer>
Desc: provides scrambles with flips/twists and cycle breaks to practice all edge and corner buffers
Aliases:
    m"""
    piece_type = 'edge' if len(buffer) == 2 else 'corner'

    if piece_type == 'edge':
        cycle_break_floats_edges(buffer)
    elif piece_type == 'corner':
        cycle_break_floats_corners(buffer)


def cycle_break_floats_edges(buffer):
    """Syntax: cbuff <edge buffer>
Desc: provides scrambles with flips and cycle breaks to practice all edge buffers"""
    # todo add corners
    while True:
        drill = Drill()
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


def cycle_break_floats_corners(buffer):
    """Syntax: cbuff <corner buffer>
Desc: provides scrambles with twists and cycle breaks to practice all corner buffers"""
    while True:
        drill = Drill()
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


def get_comm(args):
    max_list = True
    eli_list = True
    # if '-b' not in args:
    if '-e' in args:
        args.remove('-e')
        eli_list = True
        max_list = False

    elif '-m' in args:
        args.remove('-m')
        eli_list = False
        max_list = True

    buffer, *cycles = args
    buffer = buffer.upper()

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    # iterate the cycles
    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = LetterScheme().convert_pair_to_pos(buffer, cycle)
        let1, let2 = cycle
        if max_list:
            print(f"Max {let1 + let2}:", MAX_COMMS[buffer][a][b])
        if eli_list:
            print(f"Eli {let1 + let2}:", ELI_COMMS.get(buffer, {}).get(a, {}).get(b, "Not listed"))

        # should it show just the expanded ver or the comm notation?
    return buffer


def drill_twists(twist_type):
    """Drills twists: 2f: floating 2-twist, 3: 3-twist, or 3f: floating 3-twist"""
    match twist_type:
        case "2f" | "2":
            drill_generator.main("5")
        case "3":
            drill_generator.main("2")
        case "3f":
            drill_generator.main("3")


def get_help():
    # print(f"Just enter '{args}' with no addtional arguments or parameters to see the help file")
    print("Type 'name' to find out more about the function 'name'.")
    docs = """
h | help: Display help information for commands.
m | memo: Memo the cube and handle options.
ls | letterscheme: Manage letter scheme options.
b | buff | buffer: Drill buffer and handle options.
a | algs: Generate algorithm drills.
s | sticker: Drill stickers from default buffers.
q | quit | exit: Exit the program.
c | comm: Retrieve and display commutators.
reload: Reload settings and letter scheme.
timeup | time: Display the elapsed time.
alger: Generate a scramble with a specified number of algs.
f | float: Provide scrambles with flips and cycle breaks.
t: Drill twists: 2f, 3, or 3f.
    """
    print(docs)
    return


def get_query() -> Tuple[str, List[str]]:
    response = ""
    while not response:
        response = input("(3bld) ").split()

    mode, *args = response
    return mode, args


# todo use ! to repeat inputs
# todo make funcs to load or dump letterscheme
# todo make help func


# todo have it use -e for excluding letter pairs and specify if only ones are wanted by listing them after


def main():
    options = """
    1. Memo the cube (optional letter scheme)
    2. Drill list of algs
    3. Drill sticker
    4. Drill buffer
    """

    with open("settings.json") as f:
        settings = json.loads(f.read())
        letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
        # buffers = settings['buffers']
        # buffer_order = settings['buffer_order']

    last_args = ""
    last_mode = 1
    intro = 'Welcome to the Letter Pair Finder. Type help or ? to list commands.'

    start_time = time.time()
    print(intro)

    while True:
        mode, args = get_query()

        # todo capitalization

        if mode == '!r' or mode == "!":
            mode = last_mode
            args = last_args
            # todo set this

        match mode:
            case 'h' | 'help':
                print("Provides helpful information about commands")
                get_help()

            case "m" | "memo":
                if not args:
                    print(memo_cube.__doc__)
                    continue

                memo_cube(args, letter_scheme)

            case "ls" | "letterscheme":
                if not args:
                    print(set_letter_scheme.__doc__)
                    continue

                letter_scheme = set_letter_scheme(args, letter_scheme)

            # only ones left
            case "a" | "algs":
                if not args:
                    print('1 for ltct, 2 for 3 twists,', '3 for floating 3 twists,', '4 for 2 flips')
                    continue
                last_mode = args[0]

                drill_generator.main(args[0])

            # do these two auto convert
            # only ones left
            # (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -e=<cycles to exclude(secondsticker)>,
            # -i=<cycles to only include(secondsticker)>)
            case "s" | "sticker":
                # todo make this for floating too  ... hahahahaa

                sticker, *exclude = args
                drill_sticker(sticker, exclude=exclude)
                last_args = args

            # todo add auto save and load for drilling buffer like a global save file, start and continue later
            # input buffer in loc but still display letter pairs with scheme?
            # (b/buffer, <buffer name>, optional -l=(load from file) optional <filename>)
            # the save file and the saved algs to drill are different so I don't know
            case "b" | "buff" | "buffer":
                last_mode = mode
                last_args = args
                # buffer name must be location name not letterscheme
                # todo what if I wanted to use this like eil's trainer
                if not args:
                    print("Syntax: <buffer> [-l --Load]")
                    continue
                buffer, *args = args
                buffer = buffer.upper()
                filename = "drill_save.json"
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
                                continue

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
                drill_buffer(piece_type, buffer.upper(), drill_list=drill_set, random_pairs=random_pairs)

            case 'q' | 'quit' | 'exit':
                quit()

            case "c" | 'comm':
                # defaults to using max's list
                # rapid mode and change buffer

                if not args:
                    print("e.g. comm UF AB -e")
                    continue

                rapid_mode = False
                if '-r' in args:
                    rapid_mode = True
                    args.remove('-r')

                buffer = get_comm(args)

                while rapid_mode:
                    args = input("(rapid) ").split()
                    if 'quit' in args or 'exit' in args:
                        break

                    if '-b' in args:
                        buffer = args[args.index('-b') + 1]
                        args.remove('-b')
                    else:
                        args = [buffer] + args

                    get_comm(args)

            case 'reload':

                with open("settings.json") as f:
                    settings = json.loads(f.read())
                    letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
                    # buffers = settings['buffers']
                    buffer_order = settings['buffer_order']
                    all_buffers_order = buffer_order['edges'] + buffer_order['corners']
                update_comm_list(buffers=all_buffers_order)

            case 'timeup' | 'time':
                print(time.time() - start_time)

            case 'alger':
                if not args:
                    print(alger.__doc__)
                    continue
                alg_count = int(args.pop())
                alger(alg_count)

            # todo add quit to all funcs
            # todo put this stuff into a function to run

            # todo add more params
            case "f" | "float":
                if not args:
                    print(cycle_break_float.__doc__)
                    continue

                buffer = args.pop()
                cycle_break_float(buffer)

            case "t":
                if not args:
                    print(drill_twists.__doc__)
                    continue
                twist_type = args.pop()
                drill_twists(twist_type)

            case _:
                print("that option is not recognised")
    # todo fix inconsistent usage of "" and ''
    # might be best to allways store and work with letterpairs in Singmaster notation
    # todo and just convert to and from whenever loading or displaying in letterscheme
    # todo scramble gen for corners
    # todo output display class


if __name__ == "__main__":
    main()
