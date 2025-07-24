from Cube import Drill


def drill_ltct(args):
    """
    Drill ltct algs:
    -def default, -u UU, -ud UD add flags to add the set to drill or -s to drill ltct with a random scramble.
    Enter 'a' after a scramble to see the associated alg
    """

    if "-s" in args:
        Drill().drill_ltct_scramble()
    else:
        Drill().drill_ltct(args)
