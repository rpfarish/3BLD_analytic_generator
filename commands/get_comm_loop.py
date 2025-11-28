from commands.get_buffer import get_comm
from Cube.letterscheme import LetterScheme


def get_comm_loop(args, file_comms: list, letter_scheme: LetterScheme):
    """Comm: comm [buffer] [target pair] [-r]
    Description: Displays the commutator given from the imported comm sheets.
    Options:
        -r Enters rapid mode to quickly enter many comms from the same buffer.
           Enter q to exit. To change buffer, enter -b [buffer].
    Aliases:
        c
    Usage:
        comm UF AB
        (rapid) -b UFR
    """

    rapid_mode = False
    if "-r" in args:
        rapid_mode = True
        args.remove("-r")

    buffer = get_comm(args, file_comms, letterscheme=letter_scheme)
    if not buffer:
        return

    while rapid_mode:
        args = input("(rapid) ").split()
        if not args:
            continue
        if "q" == args[0] or "quit" in args or "exit" in args:
            break

        if "-b" in args:
            buffer = args[args.index("-b") + 1]
            args.remove("-b")
        else:
            args = [buffer] + args

        get_comm(args, file_comms, letterscheme=letter_scheme)
