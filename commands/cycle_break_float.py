from Cube import Drill


def cycle_break_float(buffer, buffer_order=None):
    """Syntax: rb <buffer> [ --allow-other-floats ]
    Desc: Drill random floating cycles for the input buffer with edge or corner only scrambles.
          Includes cycle breaks, and flips but not floats from other buffers.
    Options:
        --allow-other-floats Allows additional floating cycles other than input buffer
    """
    Drill().cycle_break_float(buffer, buffer_order=buffer_order)
