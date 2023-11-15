import json
import time

import drill_generator
from Commutator.convert_list_to_comms import update_comm_list
from Cube.letterscheme import LetterScheme
from operations import alger, cycle_break_float, drill_buffer, get_comm_loop, get_rand_buff
from operations import drill_sticker, drill_twists, get_help, get_query, memo_cube, set_letter_scheme


# todo settings with buffer order and alt pseudo swaps for each parity alg
# todo how to ingest a new comm sheet esp full floating
# todo convert a sheet to have any comm for any buffer ie custom buffer order

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
        buffers = settings['buffers']
        buffer_order = settings['buffer_order']
        all_buffers_order = buffer_order['edges'] + buffer_order['corners']
        if len(all_buffers_order) != 16:
            raise ValueError("Please include all of the buffers in settings.json")

        comm_file_name = settings['comm_file_name']
        parity_swap_edges = settings['parity_swap_edges']
        top_corner_key = "1st Target:"
    try:
        with open(f"comms/{comm_file_name}/{comm_file_name}.json") as f:
            file_comms = json.load(f)
    except FileNotFoundError:
        update_comm_list(buffers=all_buffers_order, file=comm_file_name, top_corner_key=top_corner_key)

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
                get_help()

            case "m" | "memo":
                if not args:
                    print(memo_cube.__doc__)
                    continue
                memo_cube(args, letter_scheme, buffers, parity_swap_edges, buffer_order)

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
            # (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -e=<cycles to exclude(secondsticker)>,
            # -i=<cycles to only include(secondsticker)>, -file=<filename>)
            case "s" | "sticker":
                # todo make this for floating too  ... hahahahaa

                sticker, *exclude = args
                drill_sticker(sticker, exclude=exclude, buffer_order=buffer_order)
                last_args = args

            case "b" | "buff" | "buffer":
                last_mode = mode
                last_args = args
                # todo what if I wanted to use this like eil's trainer
                if not args:
                    print("Syntax: <buffer> [-l --Load]")
                    continue
                buffer, *args = args
                buffer = buffer.upper()
                filename = "cache/drill_save.json"
                drill_buffer(args, filename, buffer, buffer_order, file_comms)

            case 'q' | 'quit' | 'exit':
                quit()

            case "c" | 'comm':
                if not args:
                    print("e.g. comm UF AB -e")
                    continue
                get_comm_loop(args, file_comms, comm_file_name, letter_scheme)

            case 'reload':
                with open("settings.json") as f:
                    settings = json.loads(f.read())
                    letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
                    buffer_order = settings['buffer_order']
                    all_buffers_order = buffer_order['edges'] + buffer_order['corners']
                    comm_file_name = settings['comm_file_name']
                update_comm_list(buffers=all_buffers_order, file=comm_file_name, top_corner_key=top_corner_key)

            case 'timeup' | 'time':
                print(time.time() - start_time)

            case 'alger':
                if not args:
                    print(alger.__doc__)
                    continue
                alg_count = int(args.pop())
                alger(alg_count, buffer_order=buffer_order)

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
            case "rb":
                get_rand_buff(all_buffers_order)

            case _:
                print("that option is not recognised")

    # todo fix inconsistent usage of "" and ''
    # might be best to allways store and work with letterpairs in Singmaster notation
    # todo and just convert to and from whenever loading or displaying in letterscheme
    # todo scramble gen for corners
    # todo output display class
    # todo add more params


if __name__ == "__main__":
    main()
