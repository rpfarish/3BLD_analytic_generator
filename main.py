import functools
import json
import os
import sys
import time
from contextlib import suppress
from pathlib import Path

from commands import (
    alger,
    cycle_break_float,
    drill_buffer,
    drill_cycle_break,
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
from comms.comms import COMMS
from Commutator.validate_comms import validate_comms
from Cube import Drill
from Settings.settings import Settings
from Spreadsheets import ingest_spreadsheet

# TODO: how to ingest a new comm sheet esp full floating
# TODO: Set up history file with cross-platform compatibility

readline = None

with suppress(ImportError):
    import readline

if readline is not None:
    # Put history file next to main.py
    project_root = os.path.dirname(os.path.abspath(sys.argv[0]))
    hist_file = os.path.join(project_root, "cache", "bld_generator_history")
    # Ensure cache directory exists
    os.makedirs(os.path.dirname(hist_file), exist_ok=True)

    with suppress(FileNotFoundError):
        readline.read_history_file(hist_file)
        readline.set_history_length(1000)

    import atexit

    atexit.register(functools.partial(readline.write_history_file, hist_file))

# TODO: reevaluate needing valid buffers or expand to include FU and stuff

# TODO: what is the difference between user folder and module/program source folder

# TODO: what are the files and folders that the user should be able to add and
# remove files from:

# TODO: input : Spreadsheets, drill_lists
# TODO: output: scrams
# TODO: what about settings? should it be editable from the terminal?


# TODO: should commands be a class? I feel like that might improve things as right now it feels quite functional


def clear_screen():
    """Clear the console screen"""
    os.system("cls" if os.name == "nt" else "clear")


def format_duration(seconds):
    """
    Format duration in seconds to a readable string.
    Displays only non-zero time units.
    """
    seconds = round(seconds, 2)

    if seconds < 60:
        return f"{seconds}s"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = round(seconds % 60, 2)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")

    return " ".join(parts)


def count_non_empty_leaves(d):
    count = 0
    for value in d.values():
        if isinstance(value, dict):
            count += count_non_empty_leaves(value)
        elif value != "":
            count += 1
    return count


def main():
    # TODO: add settings to readme

    try:
        settings = Settings()
        settings.letter_scheme
    except json.decoder.JSONDecodeError as e:
        print(
            "Error: Please ensure settings.json has commas at the end of lines where appropriate\n"
            "Could not decode settings.json"
        )
        print(e)
        quit()

    # TODO: add current loadable buffers json file to each folder in /comms
    # TODO: make this loop over the .csv files in the folder instead of in settings?
    # TODO:: When loading a sheet double check that the algs are correct
    # TODO:: Figure out how to deal with different buffer orders and RDF vs DFR
    # TODO:: Properly format sheets that are split (list only half of the cases)

    # Convert Spreadsheets to json
    for i, (name, data) in enumerate(settings.comm_files.items(), 1):
        if not data["enabled"]:
            continue
        comm_file_name = data["spreadsheet"]
        check_path = Path("comms") / comm_file_name / f"{comm_file_name}.json"

        if check_path.exists():
            continue

        response = input(f"Do you want to import {comm_file_name} ? (y | n): ").lower()
        if response.startswith("y"):
            ingest_spreadsheet(comm_file_name, data["cols_first"])

            comm_file = data["spreadsheet"]
            cur_comms = load_comms(file_name=comm_file)

            # Get and sort buffer order
            edge_buffer_counts = {}
            corner_buffer_counts = {}
            for buffer, comm in cur_comms.items():
                count = count_non_empty_leaves(comm)
                if len(buffer) == 2:
                    edge_buffer_counts[buffer] = count
                else:
                    corner_buffer_counts[buffer] = count

            corner_buffers = list(corner_buffer_counts.keys())
            edge_buffers = list(edge_buffer_counts.keys())

            corner_buffers = sorted(
                corner_buffers, key=lambda x: corner_buffer_counts[x], reverse=True
            )
            edge_buffers = sorted(
                edge_buffers, key=lambda x: edge_buffer_counts[x], reverse=True
            )

            for buffer in cur_comms:
                validate_comms(cur_comms, buffer, i, name, corner_buffers, edge_buffers)

            # create_full_buffer_comms()
            # validate_comms()

    # Import Spreadsheets
    file_comms = {}
    file_comms_list = []
    for i, (name, data) in enumerate(settings.comm_files.items(), 1):
        if not data["enabled"]:
            continue

        comm_file = data["spreadsheet"]

        cur_comms = load_comms(file_name=comm_file)

        file_comms_list.append((name, cur_comms))

        if (
            name == settings.floating_comms_sheet_name
            or data["name"] == settings.floating_comms_sheet_name
        ):
            file_comms = cur_comms

        # print("=" * 30, name, "=" * 30)
        #
        # directory = Path(f"comms/{comm_file}")
        # buffers = [csv_file.stem for csv_file in directory.glob("*.csv")]
        #
        # edge_buffer_counts = {}
        # corner_buffer_counts = {}
        # for buffer, comm in file_comms.items():
        #     count = count_non_empty_leaves(comm)
        #     if len(buffer) == 2:
        #         edge_buffer_counts[buffer] = count
        #     else:
        #         corner_buffer_counts[buffer] = count
        #
        # corner_buffers = list(corner_buffer_counts.keys())
        # edge_buffers = list(edge_buffer_counts.keys())
        #
        # corner_buffers = sorted(
        #     corner_buffers, key=lambda x: corner_buffer_counts[x], reverse=True
        # )
        # edge_buffers = sorted(
        #     edge_buffers, key=lambda x: edge_buffer_counts[x], reverse=True
        # )
        #
        # # TODO:: do we only validate on ingest?
        # for buffer in file_comms:
        #     validate_comms(file_comms, buffer, i, name, corner_buffers, edge_buffers)

    if not file_comms_list:
        file_comms = COMMS
        file_comms_list.append(("Comm", file_comms))

    last_args = ""
    last_mode = 1
    intro = "Welcome to the 3BLD Analytic Generator. Type help or ? to list commands."

    start_time = time.time()
    print(intro)

    while True:
        mode, args = get_query()

        # TODO: capitalization

        if mode == "!r" or mode == "!":
            mode = last_mode
            args = last_args
            # TODO: set this

        match mode:
            case "h" | "help" | "?":
                get_help()

            case "m" | "memo":
                if not args:
                    print(memo_cube.__doc__)
                    continue
                    # TODO: buffer swap
                memo_cube(args, settings)

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

            case "d" | "drill":
                # TODO: make this for floating too  ... hahahahaa
                if not args:
                    print(drill_sticker.__doc__)
                    continue
                args = [arg.lower() for arg in args]
                drill_sticker(args, buffers=settings.buffers)
                last_args = args

            case "b" | "buff" | "buffer":
                last_mode = mode
                last_args = args
                # TODO: what if I wanted to use this like eil's trainer (with UB UFL -r)
                if not args:
                    print(drill_buffer.__doc__)
                    continue
                filename = "cache/drill_save.json"
                # TODO: use default list? or maybe not if buffer list is incompatible
                # use default comms at all if buffers are super different?
                drill_buffer(
                    args,
                    file_comms,
                    filename,
                    settings.buffer_order,
                    settings.letter_scheme,
                )

            case "q" | "quit" | "exit":
                quit()

            case "c" | "comm":
                # TODO: option to input in using letterscheme but output pos notation
                if not args:
                    print(get_comm_loop.__doc__)
                    continue
                get_comm_loop(
                    args,
                    file_comms_list,
                    settings.letter_scheme,
                )

            case "cb" | "cyclebreak":
                if not args:
                    print("helps drill cycle breaks\ne.g. cb -c")
                drill_cycle_break(args, settings.buffers)

            case "reload":
                settings.reload()

            case "timeup" | "time":
                secs = time.time() - start_time
                print(format_duration(secs))

            case "alger":
                if not args:
                    print(alger.__doc__)
                    continue
                alg_count, *_ = args

                try:
                    print(alg_count, "is not a valid number")
                    alg_count = int(alg_count)
                except ValueError:
                    continue

                alger(alg_count, settings)

            case "tc":
                Drill().drill_two_color_memo(settings.buffers["corner_buffer"])

            case "rb" | "rndbfr":
                if not args:
                    print(cycle_break_float.__doc__)
                    continue
                buffer, *_ = args
                # TODO: make sure buffer is not garbage input
                cycle_break_float(buffer.upper())

            case "t" | "twist":
                if not args:
                    print(drill_twists.__doc__)
                    continue
                twist_type, *_ = args
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

    # TODO:: fix inconsistent usage of "" and ''
    # might be best to allways store and work with letterpairs in Singmaster notation
    # TODO:: and just convert to and from whenever loading or displaying in letterscheme
    # TODO:: scramble gen for corners
    # TODO:: output display class
    # TODO:: add more params
    # TODO:: add links to other alg/buffer trainers


if __name__ == "__main__":
    main()
