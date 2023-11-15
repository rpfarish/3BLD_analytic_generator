import json

from operations.drill_piece_buffer import drill_piece_buffer


def drill_buffer(args, filename, buffer, buffer_order, file_comms):
    """Syntax: <buffer> [-l --Load]"""
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
