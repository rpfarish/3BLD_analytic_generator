"""Main function entry point starts and ends here."""

import functools
import json
import logging
import sys
import time
from contextlib import suppress
from pathlib import Path

from Commands import Commands

# from commands import (
#     alger,
#     cycle_break_float,
#     drill_buffer,
#     drill_cycle_break,
#     drill_ltct,
#     drill_sticker,
#     drill_twists,
#     drill_two_flips,
#     get_comm_loop,
#     get_help,
#     get_query,
#     get_rand_buff,
#     load_comms,
#     memo_cube,
#     set_letter_scheme,
# )
# from Commutator.validate_comms import validate_comms
# from Cube import Drill
from interface import CLIInterface, OutputMode
from Settings.settings import Settings

# from Spreadsheets import ingest_spreadsheet
#
readline = None


with suppress(ImportError):
    import readline

if readline is not None:
    # Put history file next to main.py
    project_root = Path(__file__).resolve().parent
    hist_file = project_root / "cache" / "bld_generator_history"
    # Ensure cache directory exists
    hist_file.parent.mkdir(parents=True, exist_ok=True)

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


def get_query() -> tuple[str, list[str]]:
    response = ""
    while not response:
        try:
            response = input("(3bld) ").split()
        except KeyboardInterrupt:
            sys.exit()

    mode, *args = response
    return mode, args


def format_duration(seconds: float) -> str:
    """Format duration in seconds to a readable string.

    Displays only non-zero time units.
    """
    seconds = round(seconds, 2)

    SECONDS_IN_MINUTE = 60
    if seconds < SECONDS_IN_MINUTE:
        return f"{seconds}s"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = round(seconds % 60, 2)

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")

    return " ".join(parts)


#
# type Comms = dict[str, str | Comms]
#
#
# def count_non_empty_leaves(d: Comms | str) -> int:
#     """Recursively calculates the number of empty values in a nested dict."""
#     if not isinstance(d, dict) and isinstance(d, str):
#         return int(d != "")
#
#     count: int = 0
#     for value in d.values():
#         if isinstance(value, dict):
#             count += count_non_empty_leaves(value)
#         elif value != "":
#             count += 1
#     return count
#
#


def load_settings(ui: CLIInterface) -> Settings:
    """Load and validate settings with proper error handling."""
    try:
        settings = Settings(ui)
        _ = settings.letter_scheme  # Validate settings are accessible
        ui.debug("Settings loaded successfully")
    except json.decoder.JSONDecodeError as e:
        ui.error("Could not decode settings.json", e)
        ui.info(
            "Please ensure settings.json has commas"
            " at the end of lines where appropriate"
        )
        ui.blank_line()
        sys.exit(1)
    else:
        return settings


#
# def import_spreadsheets(ui: CLIInterface, settings: Settings) -> None:
#     """Convert and import spreadsheets to JSON format."""
#     ui.debug("Starting spreadsheet import process")
#
#     for i, (name, data) in enumerate(settings.comm_files.items(), 1):
#         if not data["enabled"]:
#             ui.debug(f"Skipping disabled comm file: {name}")
#             continue
#
#         comm_file_name = data["spreadsheet"]
#         check_path = Path("comms") / comm_file_name / f"{comm_file_name}.json"
#
#         if check_path.exists():
#             ui.debug(f"Using existing comm file: {check_path}")
#             continue
#
#         ui.blank_line()
#         ui.info(f"Found new spreadsheet: {comm_file_name}")
#
#         if ui.confirm(f"Do you want to import {comm_file_name}?"):
#             ui.info(f"Importing {comm_file_name}...")
#
#             ingest_spreadsheet(comm_file_name, data["cols_first"])
#             ui.success(f"Successfully imported {comm_file_name}")
#
#             # Validate the imported comms
#             comm_file = data["spreadsheet"]
#             cur_comms: Comms = load_comms(file_name=comm_file)
#
#             # Get and sort buffer order
#             edge_buffer_counts = {}
#             corner_buffer_counts = {}
#             for buffer, comm in cur_comms.items():
#                 count = count_non_empty_leaves(comm)
#                 EDGE_BUFFER_SIZE = 2
#                 if len(buffer) == EDGE_BUFFER_SIZE:
#                     edge_buffer_counts[buffer] = count
#                 else:
#                     corner_buffer_counts[buffer] = count
#
#             corner_buffers = sorted(
#                 corner_buffer_counts.keys(),
#                 key=lambda x: corner_buffer_counts[x],
#                 reverse=True,
#             )
#             edge_buffers = sorted(
#                 edge_buffer_counts.keys(),
#                 key=lambda x: edge_buffer_counts[x],
#                 reverse=True,
#             )
#
#             ui.info("Validating commutators...")
#             for buffer in cur_comms:
#                 validate_comms(cur_comms, buffer, i, name, corner_buffers, edge_buffers)
#
#             ui.success("Validation complete")
#
#         else:
#             ui.warning(f"Skipped import of {comm_file_name}")
#
#
# def load_comm_files(
#     ui: CLIInterface, settings: Settings
# ) -> tuple[Comms, list[tuple[str, Comms]]]:
#     """Load all enabled comm files."""
#     ui.debug("Loading comm files")
#
#     file_comms = {}
#     file_comms_list = []
#
#     for i, (name, data) in enumerate(settings.comm_files.items(), 1):
#         if not data["enabled"]:
#             ui.debug(f"Skipping disabled comm file: {name}")
#             continue
#
#         comm_file = data["spreadsheet"]
#
#         cur_comms = load_comms(file_name=comm_file)
#         file_comms_list.append((name, cur_comms))
#
#         if (
#             name == settings.floating_comms_sheet_name
#             or data["name"] == settings.floating_comms_sheet_name
#         ):
#             file_comms = cur_comms
#
#         ui.debug(f"Loaded comm file {i}: {name} ({len(cur_comms)} buffers)")
#
#     if not file_comms_list:
#         ui.warning("No comm files loaded, using default comms")
#         file_comms = COMMS
#         file_comms_list.append(("Comm", file_comms))
#     else:
#         ui.success(f"Loaded {len(file_comms_list)} comm file(s)")
#
#     return file_comms, file_comms_list
#
#
# def display_help(ui: CLIInterface) -> None:
#     ui.header("3BLD Analytic Generator - Command Reference")
#
#     commands = [
#         ["help, h, ?", "Display this help message"],
#         ["memo, m", "Memorize a cube scramble"],
#         ["drill, d", "Practice specific stickers"],
#         ["buffer, b, buff", "Drill buffer cases"],
#         ["comm, c", "Look up a commutator"],
#         ["algs, a", "Drill custom algorithms (comma-separated)"],
#         ["cyclebreak, cb", "Practice cycle breaks"],
#         ["twist, t", "Drill corner twists"],
#         ["flip", "Drill edge flips"],
#         ["ltct", "Last Two Corner Twist drill"],
#         ["tc", "Two-color memo drill"],
#         ["rndbfr, rb", "Random buffer cycle break"],
#         ["ltrscm, ls", "Change letter scheme"],
#         ["alger", "Generate random algorithms"],
#         ["arb", "Get random buffer"],
#         ["time, timeup", "Show session duration"],
#         ["reload", "Reload settings from file"],
#         ["clear", "Clear the screen"],
#         ["quit, q, exit", "Exit the application"],
#     ]
#
#     ui.table(headers=["Command", "Description"], rows=commands, col_widths=[20, 50])
#
#     ui.blank_line()
#     ui.info("Tip: Use '!' or '!r' to repeat the last command")
#
#
# def handle_memo_command(ui: CLIInterface, args, settings: Settings) -> None:
#     """Handle memo cube command"""
#     if not args:
#         ui.warning("No scramble provided")
#         ui.info("Usage: memo <scramble>")
#         ui.info("Example: memo R U R' U' R' F R2 U' R' U' R U R' F'")
#         return
#
#     ui.debug(f"Running memo_cube with args: {args}")
#     memo_cube(args, settings)
#     ui.success("Memo generated successfully")
#
#
# def handle_drill_command(ui: CLIInterface, args, settings):
#     """Handle sticker drill command"""
#     if not args:
#         ui.warning("No stickers specified")
#         ui.info(drill_sticker.__doc__ or "Usage: drill <stickers>")
#         return
#
#     # try:
#     args = [arg.lower() for arg in args]
#     ui.info(f"Drilling stickers: {', '.join(args)}")
#     drill_sticker(args, buffers=settings.buffers)
#     # except Exception as e:
#     # ui.error("Failed to run drill", e)
#
#
# def handle_buffer_command(ui: CLIInterface, args, file_comms, settings):
#     """Handle buffer drill command"""
#     if not args:
#         ui.warning("No buffer specified")
#         ui.info(drill_buffer.__doc__ or "Usage: buffer <buffer_name>")
#         return
#
#     try:
#         filename = "cache/drill_save.json"
#         ui.info(f"Starting buffer drill: {args[0]}")
#         drill_buffer(
#             args,
#             file_comms,
#             filename,
#             settings.buffer_order,
#             settings.letter_scheme,
#         )
#     except Exception as e:
#         ui.error("Failed to run buffer drill", e)
#
#
# def handle_comm_command(ui: CLIInterface, args, file_comms_list, settings):
#     """Handle commutator lookup command"""
#     if not args:
#         ui.warning("No commutator specified")
#         ui.info(get_comm_loop.__doc__ or "Usage: comm <letter_pair>")
#         return
#
#     try:
#         ui.debug(f"Looking up commutator: {args}")
#         get_comm_loop(args, file_comms_list, settings.letter_scheme)
#     except Exception as e:
#         ui.error("Failed to lookup commutator", e)
#
#
# def handle_algs_command(ui: CLIInterface, args):
#     """Handle custom algorithm drill command"""
#     if not args:
#         ui.warning("No algorithms provided")
#         ui.info("Usage: algs <alg1>, <alg2>, <alg3>, ...")
#         ui.info("Example: algs R U R' U', F R U' R' U' R U R' F'")
#         ui.info("Note: Algorithms must start and end in the same orientation")
#         return
#
#     try:
#         args_str = "".join(args)
#         algs_list = [" ".join(alg.split()) for alg in args_str.split(",")]
#
#         ui.info(f"Drilling {len(algs_list)} algorithm(s)")
#         ui.list_items(algs_list, numbered=True)
#         ui.blank_line()
#
#         Drill().drill_algs(algs_list)
#     except Exception as e:
#         ui.error("Failed to drill algorithms", e)
#
#
# def handle_letter_scheme_command(ui: CLIInterface, args, settings):
#     """Handle letter scheme change command"""
#     if not args:
#         ui.result("Current letter scheme", settings.letter_scheme)
#         ui.info("Usage: ltrscm <scheme_name>")
#         return
#
#     try:
#         old_scheme = settings.letter_scheme
#         settings.letter_scheme = set_letter_scheme(args, settings.letter_scheme)
#
#         if old_scheme != settings.letter_scheme:
#             ui.success(
#                 f"Letter scheme changed: {old_scheme} → {settings.letter_scheme}"
#             )
#         else:
#             ui.info(f"Letter scheme unchanged: {settings.letter_scheme}")
#     except Exception as e:
#         ui.error("Failed to change letter scheme", e)
#
#
# def handle_cycle_break_command(ui: CLIInterface, args, settings):
#     """Handle cycle break drill command"""
#     if not args:
#         ui.warning("No options specified")
#         ui.info("Usage: cb -c (for corners) or cb -e (for edges)")
#         return
#
#     try:
#         ui.info("Starting cycle break drill")
#         drill_cycle_break(args, settings.buffers)
#     except Exception as e:
#         ui.error("Failed to run cycle break drill", e)
#
#
# def handle_alger_command(ui: CLIInterface, args, settings):
#     """Handle algorithm generator command"""
#     if not args:
#         ui.warning("No algorithm count specified")
#         ui.info(alger.__doc__ or "Usage: alger <count>")
#         return
#
#     try:
#         alg_count = int(args[0])
#         ui.info(f"Generating {alg_count} algorithm(s)")
#         alger(alg_count, settings)
#     except ValueError:
#         ui.error(f"'{args[0]}' is not a valid number")
#     except Exception as e:
#         ui.error("Failed to generate algorithms", e)
#
#
# def handle_random_buffer_command(ui: CLIInterface, args):
#     """Handle random buffer cycle break command"""
#     if not args:
#         ui.warning("No buffer specified")
#         ui.info(cycle_break_float.__doc__ or "Usage: rb <buffer>")
#         return
#
#     try:
#         buffer = args[0].upper()
#         ui.info(f"Random buffer cycle break for: {buffer}")
#         cycle_break_float(buffer)
#     except Exception as e:
#         ui.error("Failed to generate random buffer", e)
#
#
def main():
    ui = CLIInterface(
        output_mode=OutputMode.COLORED, log_to_file=True, log_level=logging.DEBUG
    )

    # Load settings
    settings = load_settings(ui)

    # TODO: Make sure settings is easily globally accessible

    #
    #     # Import and load spreadsheets
    #     import_spreadsheets(ui, settings)
    #     file_comms, file_comms_list = load_comm_files(ui, settings)
    #
    #     # Track session state
    last_args = ""
    last_mode = ""
    start_time = time.time()

    # Welcome message
    ui.header("3BLD Analytic Generator")
    ui.info("Welcome! Type 'help' or '?' to list available commands.")
    ui.separator()
    ui.blank_line()

    commands = Commands(ui, settings)

    while True:
        try:
            mode, args = get_query()

            # Handle repeat command
            if mode in ("!r", "!"):
                if not last_mode:
                    ui.warning("No previous command to repeat")
                    continue
                mode = last_mode
                args = last_args
                ui.info(f"Repeating: {mode} {' '.join(args)}")

            ui.debug(f"Running command: {mode}, with args {args}")

            match mode:
                #                 case "h" | "help" | "?":
                #                     get_help(ui)
                #                     last_mode = mode
                #                     last_args = args
                #
                case "m" | "memo":
                    commands.memo(args)
                #
                #                 case "ls" | "ltrscm":
                #                     handle_letter_scheme_command(ui, args, settings)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "a" | "algs":
                #                     handle_algs_command(ui, args)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "d" | "drill":
                #                     handle_drill_command(ui, args, settings)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "b" | "buff" | "buffer":
                #                     handle_buffer_command(ui, args, file_comms, settings)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "c" | "comm":
                #                     handle_comm_command(ui, args, file_comms_list, settings)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "cb" | "cyclebreak":
                #                     handle_cycle_break_command(ui, args, settings)
                #                     last_mode = mode
                #                     last_args = args
                #
                #                 case "reload":
                #                     ui.info("Reloading settings...")
                #                     settings.reload()
                #                     ui.success("Settings reloaded successfully")
                #
                #                 case "timeup" | "time":
                #                     secs = time.time() - start_time
                #                     ui.result("Session duration", format_duration(secs))
                #
                #                 case "alger":
                #                     handle_alger_command(ui, args, settings)
                #
                #                 case "tc":
                #                     try:
                #                         ui.info("Starting two-color memo drill")
                #                         Drill().drill_two_color_memo(settings.buffers["corner_buffer"])
                #                     except Exception as e:
                #                         ui.error("Failed to run two-color drill", e)
                #
                #                 case "rb" | "rndbfr":
                #                     handle_random_buffer_command(ui, args)
                #
                #                 case "t" | "twist":
                #                     if not args:
                #                         ui.warning("No twist type specified")
                #                         ui.info(drill_twists.__doc__ or "Usage: twist <type>")
                #                         return
                #
                #                     try:
                #                         twist_type = args[0]
                #                         ui.info(f"Starting twist drill: {twist_type}")
                #                         drill_twists(twist_type)
                #                     except Exception as e:
                #                         ui.error("Failed to run twist drill", e)
                #
                #                 case "ltct":
                #                     if not args:
                #                         ui.info(drill_ltct.__doc__ or "Usage: ltct <options>")
                #                         continue
                #                     ui.info("Starting LTCT drill")
                #                     drill_ltct(args)
                #
                #                 case "arb":
                #                     ui.info("Getting random buffer...")
                #                     get_rand_buff(settings.all_buffers_order)
                #
                #                 case "flip":
                #                     ui.info("Starting edge flip drill")
                #                     drill_two_flips()
                #
                #                 case "clear":
                #                     ui.clear_screen()
                #
                case "q" | "quit" | "exit":
                    ui.blank_line()
                    ui.info("Thanks for using 3BLD Analytic Generator!")
                    ui.result(
                        "Total session time", format_duration(time.time() - start_time)
                    )
                    ui.blank_line()
                    sys.exit(0)
                #
                case _:
                    ui.error(f"Unrecognized command: '{mode}'")
                    ui.info("Type 'help' for a list of available commands")
                    continue

        except KeyboardInterrupt:
            ui.blank_line()
            if ui.confirm("Are you sure you want to quit?", default=False):
                ui.info("Goodbye!")
                sys.exit(0)
            else:
                ui.info("Continuing...")
                continue

            # except Exception as e:
            #     ui.error("An unexpected error occurred", e)
            #     ui.info("Type 'help' for available commands or 'quit' to exit")

            last_mode = mode
            last_args = args


#
if __name__ == "__main__":
    main()
    # TODO: enable memo
    # TODO: enable drill
    # TODO: enable settings
    # TODO: getting comms from a sheet
