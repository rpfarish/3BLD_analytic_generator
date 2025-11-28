import json
import os
import sys
import time
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
from Commutator.validate_comms import validate_comms
from Cube import Drill
from Settings.settings import Settings
from Spreadsheets import ingest_spreadsheet

# todo how to ingest a new comm sheet esp full floating

# Set up history file with cross-platform compatibility
try:
    import readline

    readline_available = True
except ImportError:
    # readline is not available on Windows by default
    readline_available = False
    try:
        # Try pyreadline3 as an alternative for Windows
        import pyreadline3 as readline

        readline_available = True
    except ImportError:
        pass

if readline_available:
    # Use platform-appropriate config directory
    if sys.platform == "win32":
        # Windows: Try APPDATA, then USERPROFILE, then fallback
        config_dir = (
            os.environ.get("APPDATA")
            or os.environ.get("USERPROFILE")
            or os.path.expanduser("~")
        )
        histfile = os.path.join(config_dir, "bld_generator_history")
    elif sys.platform == "darwin":
        # macOS: Use ~/Library/Application Support
        config_dir = os.path.expanduser("~/Library/Application Support")
        histfile = os.path.join(config_dir, "bld_generator_history")
    else:
        # Linux and other Unix-like: Use XDG or fallback to home
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        histfile = os.path.join(config_dir, "bld_generator_history")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(histfile), exist_ok=True)

    try:
        readline.parse_and_bind("C-p: previous-history")
        readline.parse_and_bind("C-n: next-history")
    except OSError:
        pass

    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except (FileNotFoundError, PermissionError, OSError):
        # File doesn't exist, no permissions, or binding not supported
        pass
    # Register cleanup function to save history on exit
    import atexit

    try:
        import atexitmain
    except ModuleNotFoundError:
        pass

    atexit.register(lambda: readline.write_history_file(histfile))
else:
    # print("Warning: readline not available. Command history will not be saved.")
    histfile = None


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
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0:
        parts.append(f"{secs}s")

    return " ".join(parts)


def check_comm_sheets_exist(path) -> bool:
    return os.path.isfile(path)


def main():
    # todo add settings to readme

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

    # todo add current loadable buffers json file to each folder in /comms
    # todo make this loop over the .csv files in the folder instead of in settings?
    # TODO: When loading a sheet double check that the algs are correct
    # TODO: Figure out how to deal with different buffer orders and RDF vs DFR
    # TODO: Properly format sheets that are split (list only half of the cases)

    for name, data in settings.comm_files.items():
        # Path("Spreadsheets/mycoolcoms.txt")
        # Construct the path: comms/mycoolcoms.txt/mycoolcoms.txt.json
        comm_file_name = data["spreadsheet"]
        check_path = Path("comms") / comm_file_name / f"{comm_file_name}.json"

        if check_path.exists():
            continue

        response = input(f"Do you want to import {comm_file_name} ? (y | n): ").lower()
        if response.startswith("y"):
            ingest_spreadsheet(comm_file_name, settings, data["cols_first"])
            # create_full_buffer_comms()
            # validate_comms()

    # check file_comms usage and switch some of them to default comms which I haven't made yet
    # TODO: redownload max xlsx

    file_comms_list = []
    for i, (name, data) in enumerate(settings.comm_files.items()):
        print("=" * 30, name, "=" * 30)
        comm_file = data["spreadsheet"]
        file_comms = load_comms(file_name=comm_file)
        directory = Path(f"comms/{comm_file}")
        buffers = [csv_file.stem for csv_file in directory.glob("*.csv")]

        for buffer in file_comms:
            validate_comms(file_comms, buffer, i, name)
        file_comms_list.append((name, file_comms))

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
            case "h" | "help" | "?":
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

            case "d" | "drill":
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
                    print(drill_buffer.__doc__)
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
