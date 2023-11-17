import time

from Cube import Drill
from Settings.settings import Settings
from commands import (alger, cycle_break_float, drill_buffer, drill_ltct, drill_sticker, drill_twists, drill_two_flips,
                      get_comm_loop, get_help, get_query, get_rand_buff, load_comms, memo_cube, set_letter_scheme,
                      )


# todo how to ingest a new comm sheet esp full floating

# todo use ! to repeat inputs
# todo make help func


# todo have it use -e for excluding letter pairs and specify if only ones are wanted by listing them after


def main():
    # todo add settings to readme

    settings = Settings()

    file_comms = load_comms(settings.all_buffers_order, file_name=settings.comm_file_name)
    eli_comms = load_comms(settings.all_buffers_order, file_name='eli_comms')

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
                    # todo buffer swap
                memo_cube(
                    args, settings.letter_scheme, settings.buffers, settings.parity_swap_edges,
                    settings.buffer_order
                )

            case "ls" | "letterscheme":
                if not args:
                    print(set_letter_scheme.__doc__)
                    continue
                settings.letter_scheme = set_letter_scheme(args, settings.letter_scheme)

            # only ones left
            case "a" | "algs":
                if not args:
                    print('enter algs to drill separated by a comma')
                    print('and the alg must start and end in the same orientation')
                    continue
                last_mode = args[0]
                print(args)
                args = "".join(args)
                Drill().drill_algs(args.split(','))

            # do these two auto convert
            # (s/sticker, <piece type(e/edge, c/corner)>, sticker name, optional -e=<cycles to exclude(secondsticker)>,
            # -i=<cycles to only include(secondsticker)>, -file=<filename>)
            case "s" | "sticker":
                # todo make this for floating too  ... hahahahaa

                drill_sticker(args, buffers=settings.buffers)
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
                drill_buffer(args, filename, buffer, settings.buffer_order, file_comms)

            case 'q' | 'quit' | 'exit':
                quit()

            case "c" | 'comm':
                if not args:
                    print("e.g. comm UF AB -e")
                    continue
                get_comm_loop(args, file_comms, eli_comms, settings.comm_file_name, settings.letter_scheme)

            case 'reload':
                settings.reload()

            case 'timeup' | 'time':
                print(time.time() - start_time)

            case 'alger':
                if not args:
                    print(alger.__doc__)
                    continue
                alg_count = int(args.pop())
                alger(alg_count, buffer_order=settings.buffer_order)

            case "f" | "float":
                if not args:
                    print(cycle_break_float.__doc__)
                    continue
                buffer = args.pop()
                cycle_break_float(buffer)

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

            case "rb":
                get_rand_buff(settings.all_buffers_order)

            case "flip":
                drill_two_flips()

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
