from typing import Tuple, List


def get_query() -> Tuple[str, List[str]]:
    response = ""
    while not response:
        response = input("(3bld) ").split()

    mode, *args = response
    return mode, args
