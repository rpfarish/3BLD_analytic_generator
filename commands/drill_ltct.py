from Cube import Drill


def drill_ltct(args):
    """LTCT: ltct [-u] [-ud] [-s] [-def]
    Description:
        Drill LTCT algs either UU or parital UD.
        Can also generate scrambles with UU cases.
        Default is both UU and partial UD combined.

        Add flags to add the set to drill or -s to
        drill ltct with a random scramble.
        Enter 'a' after a scramble to see the
        associated alg. (Please just use Andy's instead)

    Options:
        -def default,
        -u UU,
        -ud UD
    Usage:
        ltct -u
        ltct -ud
        ltct -u -ud
        ltct -s
    """

    if "-s" in args:
        Drill().drill_ltct_scramble()
    else:
        Drill().drill_ltct(args)
