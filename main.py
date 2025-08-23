import atexit
import os
import readline
import time

from commands import (
    alger,
    cycle_break_float,
    drill_buffer,
    drill_ltct,
    drill_sticker,
    drill_twists,
    drill_two_flips,
    get_comm_loop,
    get_help,
    get_query,
    get_rand_buff,
    load_comms,
    memo_cube,
    set_letter_scheme,
)
from Cube import Drill
from Settings.settings import Settings
from Spreadsheets import ingest_spreadsheet

# todo how to ingest a new comm sheet esp full floating

# todo use ! to repeat inputs


# todo have it use -e for excluding letter pairs and specify if only ones are wanted by listing them after

readline.parse_and_bind("C-p: previous-history")
readline.parse_and_bind("C-n: next-history")

# Set up history file
histfile = os.path.join(os.path.expanduser("~"), ".bld_generator")
try:
    readline.read_history_file(histfile)
    # Default history len is -1 (infinite), which may grow unruly
    readline.set_history_length(1000)
except FileNotFoundError:
    pass

# Save history on exit
atexit.register(readline.write_history_file, histfile)


def clear_screen():
    """Clear the console screen"""
    os.system("cls" if os.name == "nt" else "clear")


def check_comm_sheets_exist(path) -> bool:
    return os.path.isfile(path)


def main():
    # todo add settings to readme

    settings = Settings()
    settings.letter_scheme

    # todo add current loadable buffers json file to each folder in /comms
    # todo make this loop over the .csv files in the folder instead of in settings?
    for i, comm_file_name in enumerate(settings.comm_files.copy()):
        if not check_comm_sheets_exist(f"comms/{comm_file_name}/{comm_file_name}.json"):
            response = input(
                f"Do you want to import {comm_file_name} ? (y | n): "
            ).lower()
            if response.startswith("y"):
                ingest_spreadsheet(f"{comm_file_name}", settings)
            else:
                settings.comm_files.pop(i)
    # check file_comms usage and switch some of them to default comms which I haven't made yet
    file_comms_list = []
    for comm_file in settings.comm_files:
        file_comms = load_comms(settings.all_buffers_order, file_name=comm_file)
        file_comms_list.append(file_comms)

    last_args = ""
    last_mode = 1
    intro = "Welcome to the 3BLD Analytic Generator. Type help or ? to list commands."

    start_time = time.time()
    print(intro)

    while True:
        mode, args = get_query()

        # todo capitalization

        if mode == "!r" or mode == "!":
            mode = last_mode
            args = last_args
            # todo set this

        match mode:
            case "h" | "help" | "":
                get_help()

            case "m" | "memo":
                if not args:
                    print(memo_cube.__doc__)
                    continue
                    # todo buffer swap
                memo_cube(
                    args,
                    settings.letter_scheme,
                    settings.buffers,
                    settings.parity_swap_edges,
                    settings.buffer_order,
                )

            case "ls" | "ltrscm":
                if not args:
                    print(set_letter_scheme.__doc__)
                    continue
                settings.letter_scheme = set_letter_scheme(args, settings.letter_scheme)

            # only ones left
            case "a" | "algs":
                if not args:
                    print("enter algs to drill separated by a comma")
                    print("and the alg must start and end in the same orientation")
                    continue
                last_mode = args[0]
                print(args)
                args = "".join(args)
                print(f"{args=}")
                algs_list = [" ".join(alg.split()) for alg in args.split(",")]
                print(algs_list)
                Drill().drill_algs(algs_list)

            # do these two auto convert
            # (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -e=<cycles to exclude(secondsticker)>,
            # -i=<cycles to only include(secondsticker)>, -file=<filename>)
            case "s" | "stkr":
                # todo make this for floating too  ... hahahahaa
                if not args:
                    print(drill_sticker.__doc__)
                    continue
                args = [arg.lower() for arg in args]
                drill_sticker(args, buffers=settings.buffers)
                last_args = args

            case "b" | "buff" | "buffer":
                last_mode = mode
                last_args = args
                # todo what if I wanted to use this like eil's trainer (with UB UFL -r)
                if not args:
                    print("Syntax: <buffer> [-l --Load]")
                    continue
                buffer, *args = args
                buffer = buffer.upper()
                filename = "cache/drill_save.json"
                # todo use default list? or maybe not if buffer list is incompatible
                # use default comms at all if buffers are super different?
                drill_buffer(
                    args,
                    filename,
                    buffer,
                    settings.buffer_order,
                    file_comms,
                    settings.letter_scheme,
                )

            case "q" | "quit" | "exit":
                quit()

            case "c" | "comm":
                # todo option to input in using letterscheme but output pos notation
                if not args:
                    print("e.g. comm UF AB -e")
                    continue
                get_comm_loop(
                    args,
                    file_comms_list,
                    file_comms,
                    settings.comm_files,
                    settings.letter_scheme,
                )

            case "reload":
                settings.reload()

            case "timeup" | "time":
                print(time.time() - start_time)

            case "alger":
                if not args:
                    print(alger.__doc__)
                    continue
                alg_count = int(args.pop())
                alger(alg_count, buffer_order=settings.buffer_order)

            case "tc":
                Drill().drill_two_color_memo()

            case "rb" | "rndbfr":
                if not args:
                    print(cycle_break_float.__doc__)
                    continue
                buffer = args.pop()
                cycle_break_float(buffer.upper())

            case "t" | "twist":
                if not args:
                    print(drill_twists.__doc__)
                    continue
                twist_type = args.pop()
                drill_twists(twist_type)

            case "ltct":
                if not args:
                    print(drill_ltct.__doc__)
                    continue
                drill_ltct(args)

            case "arb":
                get_rand_buff(settings.all_buffers_order)

            case "flip":
                drill_two_flips()

            case "clear":
                clear_screen()

            case _:
                print("that option is not recognised")

    # todo fix inconsistent usage of "" and ''
    # might be best to allways store and work with letterpairs in Singmaster notation
    # todo and just convert to and from whenever loading or displaying in letterscheme
    # todo scramble gen for corners
    # todo output display class
    # todo add more params
    # todo add links to other alg/buffer trainers


if __name__ == "__main__":
    main()
