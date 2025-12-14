from Cube.solution import Solution
from Scramble import get_scramble


def alger(alg_count, settings):
    # TODO:: check this
    """Syntax: alger <alg count>
    Desc: generates a scramble with specified number of algs
    Note: recommended alg range is 7-13 (still needs checking)"""
    while True:
        scramble = ""
        cur_alg_count = 0
        while cur_alg_count != alg_count:
            scramble = get_scramble.get_scramble()
            cur_alg_count = Solution(
                scramble=scramble, settings=settings
            ).count_number_of_algs()

        print(scramble)
        input()
