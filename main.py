import json
from pprint import pprint

import dlin

import drill_generator
from Cube import Cube
from Cube.drill import Drill
from Cube.letterscheme import LetterScheme
from eli_comms import ELI_COMMS
from max_comms import MAX_COMMS
from solution import Solution

# print("Please select an option")
# todo settings with buffer order and alt pseudo swaps for each parity alg

options = """
1. Memo the cube (optional letter scheme)
2. Drill list of algs
3. Drill sticker
4. Drill buffer
"""


# 5. Drill 3-twists


def memo(scramble, letter_scheme):
    Solution(scramble, letter_scheme=letter_scheme).display()
    pprint(dlin.trace(scramble))


def memo_cube(scramble, letter_scheme):
    if scramble.startswith('-f'):
        _, file_name = scramble.split()
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        with open(file_name) as f:
            for num, scram in enumerate(f.readlines(), 1):
                print("Scramble number:", num)
                pprint(memo(scram.strip("\n").strip(), letter_scheme))
    elif '-fs' in scramble:
        scramble = scramble.split()
        f_index = scramble.index('-fs')
        file_name = scramble[f_index + 1]
        scramble = scramble[:f_index]
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        scramble = " ".join(scramble)

        with open(file_name, 'a+') as f:
            f.write(scramble)
            f.write("\n")
            f.close()

        memo(scramble, letter_scheme)
    else:
        memo(scramble, letter_scheme)


def drill_sticker(piece_type, sticker, buffer=None, exclude=None):
    # todo specify some cycles you want to drill more than others
    if exclude is None:
        exclude = set()
    if piece_type == 'e':
        # todo fix so it can parse args properly
        print(len(sticker), len(sticker) == 1, sticker)
        ls = letter_scheme if len(sticker) == 1 else None
        cycles_to_exclude = {sticker + piece for piece in exclude}
        sticker_scrambles = Drill().drill_edge_sticker(sticker_to_drill=sticker, return_list=False,
                                                       cycles_to_exclude=cycles_to_exclude)
        print(sticker_scrambles)
    elif piece_type == 'c':
        ls = letter_scheme if len(sticker) == 1 else LetterScheme(use_default=True)
        cycles_to_exclude = {sticker + piece for piece in exclude}
        sticker_scrambles = Cube(ls=ls).drill_corner_sticker(sticker, return_list=False,
                                                             cycles_to_exclude=cycles_to_exclude)
        print(sticker_scrambles)
    else:
        print("sorry not a valid piece type")


def drill_buffer(piece_type: str, buffer: str, drill_list: set | None):
    if piece_type == 'e':
        Drill().drill_edge_buffer(edge_buffer=buffer, translate_memo=True, drill_set=drill_list)
    if piece_type == 'c':
        Drill().drill_corner_buffer(corner_buffer=buffer, translate_memo=True)


scramble = "F2 D2 R' D2 F2 R2 U2 B2 L2 R B' U' R F' D R U' B' D' L"
scramble = "U F2 U L2 F2 D' F2 D' L2 D' F2 U' R' D' B' D2 R' D' R B U'"

import cmd


# todo letterscheme
# todo change which lists are displayed when the buffer is drilled

class LetterPairFinder(cmd.Cmd):
    intro = 'Welcome to the Letter Pair Finder. Type help or ? to list commands.'
    prompt = '(3bld) '

    def do_m(self, scramble):
        """See memo for more info"""
        self.do_memo(scramble)

    def do_memo(self, scramble: str):
        """Syntax: Memo <scramble> <[-f filename] | [-fs filename]>
        -f: displays the memorization for all scrambles in <filename>.txt
        -fs: displays the memorization for the entered scramble and saves it to <filename>.txt
        """
        if not scramble:
            print("Syntax: <scramble> <[-f filename] | [-fs filename]>")
            return
        if scramble.startswith('-f'):
            _, file_name = scramble.split()
            file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
            with open(file_name) as f:
                for num, scram in enumerate(f.readlines(), 1):
                    print("Scramble number:", num)
                    pprint(self.memo(scram.strip("\n").strip()))
        elif '-fs' in scramble:
            scramble = scramble.split()
            f_index = scramble.index('-fs')
            file_name = scramble[f_index + 1]
            scramble = scramble[:f_index]
            file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
            scramble = " ".join(scramble)

            with open(file_name, 'a+') as f:
                f.write(scramble)
                f.write("\n")
                f.close()

            pprint(self.memo(scramble))
        else:
            pprint(self.memo(scramble))

    def memo(self, scramble):
        memo_cube(scramble, letter_scheme, buffers)
        return dlin.trace(scramble)

    def do_quit(self, _):
        quit()

    def do_ls(self, args):
        if args:
            pass


def get_comm(args):
    max_list = True
    eli_list = True
    # if '-b' not in args:
    buffer, *cycles = args

    if '-e' in args:
        args.remove('-e')
        eli_list = True
        max_list = False

    elif '-m' in args:
        args.remove('-m')
        eli_list = False
        max_list = True

    buffer = buffer.upper()

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    # iterate the cycles
    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = letter_scheme.convert_pair_to_pos(buffer, cycle)
        let1, let2 = cycle
        if max_list:
            print(f"Max {let1 + let2}:", MAX_COMMS[buffer][a][b])
        if eli_list:
            print(f"Eli {let1 + let2}:", ELI_COMMS[buffer][a][b])

        # should it show just the expanded ver or the comm notation?
    return buffer


# LetterPairFinder().cmdloop()
# todo use ! to repeat inputs
# todo make funcs to load or dump letterscheme
# todo make help func

last_args = ""
last_mode = 1
intro = 'Welcome to the Letter Pair Finder. Type help or ? to list commands.'
# todo have it use -e for excluding letter pairs and specify if only ones are wanted by listing them after


# load letterscheme

with open("settings.json") as f:
    settings = json.loads(f.read())
    letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
    buffers = settings['buffers']

print(intro)

while True:
    response = input("(3bld) ").split()
    if not response:
        continue

    mode, *args = response
    # print("mode", mode, args)
    # todo capitalization
    if mode == '!r' or mode == "!":
        mode = last_mode
        args = last_args
        # todo set this

    # (m/memo, optional scramble, optional -file <filename>)
    if mode == "m" or mode == "memo":
        if not args:
            print("Syntax: <scramble> <[-f filename] | [-fs filename]>")
            continue

        last_mode = mode
        last_args = args

        args = " ".join(args)
        memo_cube(args, letter_scheme)

    elif mode == "ls":
        if 'dump' in args:
            pprint(letter_scheme.get_all_dict(), sort_dicts=False)
            letter_scheme = LetterScheme(use_default=True)
        if 'load' in args:
            with open("settings.json") as f:
                settings = json.loads(f.read())
                letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
            pprint(letter_scheme.get_all_dict(), sort_dicts=False)


    # (a/algs, type)
    elif mode == "a" or mode == "algs":
        last_mode = mode
        # mode = get_input('1 for ltct, 2 for 3 twists2'
        #                  '2')
        drill_generator.main(mode)


    # do these two auto convert

    # (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -e=<cycles to exclude(secondsticker)>, -i=<cycles to only include(secondsticker)>)
    elif mode == "s" or mode == "sticker":

        last_mode = mode
        piece_type = input("e for edges or c for corners: ").lower()
        args = input("sticker to drill (letter scheme or e.g. UR) (put to exclude after (must be same type)): ")
        if args == "!" or args == "!r":
            args = last_args
            print(last_args)

        sticker, *exclude = args.upper().split()
        drill_sticker(piece_type, sticker, exclude=exclude)
        last_args = args

    # todo add auto save and load for drilling buffer like a global save file, start and continue later
    # input buffer in loc but still display letter pairs with scheme?
    # (b/buffer, <buffer name>, optional -f=(load from file) optional <filename>)
    # the save file and the saved algs to drill are different so idk
    elif mode == "b" or mode == 'buff' or mode == "buffer":
        last_mode = mode
        last_args = args
        # buffer name must be location name not letterscheme
        if not args:
            print("Syntax: <buffer> [-l --Load]")
            continue

        buffer, *args = args
        buffer = buffer.upper()

        if '-l' in args or '--Load' in args:
            # load file
            print("Loading drill_save.json")
            with open(f"drill_save.json", "r+") as f:
                drill_list = json.load(f)
                buffer_drill_list = drill_list.get(buffer)
                if buffer_drill_list is None or not buffer_drill_list:
                    print("Savefile empty for that buffer")
                    print(f"Adding {buffer} to savefile")
                    drill_list[buffer] = []
                    f.close()
            with open(f"drill_save.json", "w") as f:
                json.dump(drill_list, f, indent=4)
            drill_set = set(drill_list[buffer])
            print("lenof drill set", len(drill_set))
        else:
            drill_set = None

        # to load 1. Buffer 2. Remaining cycles

        piece_type = 'c' if len(buffer) == 3 else 'e'
        some_random_set = None
        drill_buffer(piece_type, buffer.upper(), drill_list=drill_set)

    elif mode == 'q' or mode == 'quit' or mode == 'exit':
        quit()

    elif mode == "c" or mode == 'comm':
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

    else:
        print("that option is not recognised")
