import random


def get_scramble(requires_parity: bool = False):
    if requires_parity:
        pass
    return gen_premove(20, 21, requires_parity=requires_parity)


def gen_premove(min_len: int = 1, max_len: int = 3, requires_parity: bool = False):
    faces = ["U", "L", "F", "R", "B", "D"]
    directions = ["", "'", "2"]
    turns = []
    if max_len < 1:
        raise ValueError("max_len must be greater than 0")
    if min_len > max_len:
        raise ValueError("min_len cannot be greater than max len")
    scram_len = random.randint(min_len, max_len)
    opp = {
        "U": "D",
        "D": "U",
        "F": "B",
        "B": "F",
        "L": "R",
        "R": "L",
    }

    # first turn
    turn = random.choice(faces)
    direction = random.choice(directions)
    scramble = [turn + direction]
    turns.append(turn)

    for turn_num in range(1, scram_len):
        direction = random.choice(directions)
        last_turn = turns[turn_num - 1]
        while turn == last_turn or (
            opp[turn] == last_turn and turns[turn_num - 2] == opp[last_turn]
        ):
            turn = random.choice(faces)
        scramble.append(turn + direction)
        turns.append(turn)

    joined_scramble = " ".join(scramble)

    has_parity = (len(scramble) - joined_scramble.count("2")) % 2 == 1

    if not requires_parity:
        return joined_scramble

    if requires_parity and not has_parity:
        return gen_premove(
            min_len=min_len, max_len=max_len, requires_parity=requires_parity
        )
    if requires_parity and has_parity:
        return joined_scramble
