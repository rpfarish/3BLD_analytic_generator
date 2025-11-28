from Cube import Drill


def drill_twists(twist_type):
    """Drill twists: t [type]
    Description:
        Drill all possible 2 and 3 twists, both floating
        and non-floating.
    Options:
        2f floating 2-twist
        3  3-twist
        3f floating 3-twist
    Not Implemented:
        2 2-twist
    Usage:
        t 2f
        t 3
    """
    Drill().drill_twists(twist_type)
