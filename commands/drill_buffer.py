import json
import os

from commands.drill_piece_buffer import drill_piece_buffer
from Cube.letterscheme import sort_face_precedence


def drill_buffer(args: list[str], file_comms, filename, buffer_order, letter_scheme):
    """Buffer: buffer [buffer] [-l] [-r] [--export] [-n]
    Description: Drill all floating cycles for the input buffer
        with edge or corner only scrambles. Progress is saved to
        a file, and can be loaded using -l. Usually drills a pair
        only once, but with -r you can drill random pairs indefinitely.
        When using --export and -r, -n (number of scrambles)
        must also be specified to avoid running forever.
    Options:
        -l       Loads the comm progress from a .json file
        -r       Enables random pairs
        --export Generates a text file of all scrambles to drill
                 all pairs of the given buffer.
        -n       When using --export and -r, -n specifies the number scrambles

    Aliases:
        b
        buff
        buffer
    Usage:
        buff UFR
        b UL -l
    """
    buffer, *args = args
    buffer = buffer.upper()
    buffer = sort_face_precedence(buffer)

    # if buffer not in buffer_order["edges"] and buffer not in buffer_order["corners"]:
    #     print(
    #         f"Error: '{buffer}' must be a buffer in the buffer_order in settings.json"
    #     )
    #     return

    drill_set = None
    random_pairs = False
    return_list = False
    number_of_scrambles = 0
    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(f"{filename}", "w+") as f:
            f.write('{"description": "Saves states of drilling buffers"}')

    if "--export" in args:
        return_list = True

    if "--export" in args and "-r" in args and "-n" not in args:
        print("Warning: This command will run forever")
        print("You need to add -n [number] for the number of scrambles")

    if "-n" in args:
        number_of_scrambles = int(args[args.index("-n") + 1])

    if "-r" in args:
        random_pairs = True
    elif "-l" not in args:
        has_content = False
        with open(f"{filename}", "r") as f:
            drill_list = json.load(f)
            buffer_drill_list = drill_list.get(buffer, [])
            if len(buffer_drill_list) > 0:
                has_content = True
                print("Buffer drill file is not empty for that buffer")
                print(len(buffer_drill_list), "comms remaining")
                print("Continuing will result the rewriting of the buffer drill file")
                print("To load the drill file add '-l' to the command")
                response = input("Are you sure you want to continue y/n?: ").lower()
                if response not in ["y", "yes"]:
                    print("Aborting...")
                    return
        if has_content:
            drill_list[buffer] = []  # Modify the drill_list we already loaded
            with open(f"{filename}", "w") as f:
                json.dump(drill_list, f, indent=2)

    elif "-l" in args:
        if len(args) > 1:
            filename = args.index("-l") + 1

        # load file
        print("Loading drill_save.json")
        with open(f"{filename}", "r+") as f:
            drill_list = json.load(f)
            buffer_drill_list = drill_list.get(buffer)
            if buffer_drill_list is None or not buffer_drill_list:
                print("Savefile empty for that buffer")
                print(f"Adding {buffer} to savefile")
                drill_list[buffer] = []

        with open(f"{filename}", "w") as f:
            json.dump(drill_list, f, indent=2)

        drill_set = set(drill_list[buffer])

    # to load 1. Buffer 2. Remaining cycles
    piece_type = "c" if len(buffer) == 3 else "e"
    drill_piece_buffer(
        file_comms,
        piece_type,
        buffer.upper(),
        drill_list=drill_set,
        random_pairs=random_pairs,
        buffer_order=buffer_order,
        letter_scheme=letter_scheme,
        return_list=return_list,
        number_of_scrambles=number_of_scrambles,
    )
