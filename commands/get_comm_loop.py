from Cube.letterscheme import LetterScheme
from commands.get_buffer import get_comm


def get_comm_loop(
    args, file_comms: list, eli_comms, comm_file_name: list, letter_scheme: LetterScheme
):
    rapid_mode = False
    if "-r" in args:
        rapid_mode = True
        args.remove("-r")

    buffer = get_comm(
        args, file_comms, eli_comms, comm_file_name, letterscheme=letter_scheme
    )

    while rapid_mode:
        args = input("(rapid) ").split()
        if "quit" in args or "exit" in args:
            break

        if "-b" in args:
            buffer = args[args.index("-b") + 1]
            args.remove("-b")
        else:
            args = [buffer] + args

        get_comm(
            args, file_comms, comm_file_name, eli_comms, letterscheme=letter_scheme
        )
