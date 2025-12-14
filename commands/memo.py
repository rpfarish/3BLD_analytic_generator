from Cube.solution import Solution


def memo(scramble, settings):
    if not scramble:
        return
    # TODO:: cleanup memo output
    s = Solution(scramble, settings)
    s.display()
