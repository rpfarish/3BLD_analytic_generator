from Cube import Drill


def drill_ltct(args):
    """default, U, UD"""
    if "-s" in args:
        Drill().drill_ltct_scramble()
    else:
        Drill().drill_ltct(args)
