from Cube import Drill


def cycle_break_float(buffer, buffer_order=None):
    """Syntax: rb [buffer] [ --allow-other-floats ]
    Description: Drill random floating cycles for
        the input buffer with edge or corner only scrambles.
        Includes cycle breaks, and flips but not floats from other buffers.
        Will produce scrambles indefinitely.
    Options:
    Not Implemented:
        --allow-other-floats Allows additional floating cycles other than input buffer
    Aliases:
        rb
        rndbfr
    Usage:
        rb UF
    """
    Drill().cycle_break_float(buffer, buffer_order=buffer_order)
