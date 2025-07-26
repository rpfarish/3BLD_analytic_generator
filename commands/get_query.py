from typing import List, Tuple


def get_query() -> Tuple[str, List[str]]:
    response = ""
    while not response:
        try:
            response = input("(3bld) ").split()
        except KeyboardInterrupt:
            quit()

    mode, *args = response
    return mode, args
