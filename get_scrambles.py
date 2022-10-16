import random


def invert_solution(s):
    if not s:
        return ""

    s = s.rstrip('\n').strip().split(' ')[:]
    inverse = []
    for move in reversed(s):
        if move.endswith("'"):
            inverse.append(move.strip("'"))
        elif move.endswith("2"):
            inverse.append(move)
        else:
            inverse.append(move + "'")
    return " ".join(inverse)


def get_scramble():
    return gen_premove(20, 20)


def gen_premove(min_len=1, max_len=3):
    faces = ['U', 'L', 'F', 'R', 'B', 'D']
    directions = ["", "'", "2"]
    turns = []
    if max_len < 1:
        raise ValueError("max_len must be greater than 0")
    if min_len > max_len:
        raise ValueError("min_len cannot be greater than max len")
    scram_len = random.randint(min_len, max_len)
    opp = {'U': 'D', 'D': 'U',
           'F': 'B', 'B': 'F',
           'L': 'R', 'R': 'L',
           }

    # first turn
    turn = random.choice(faces)
    direction = random.choice(directions)
    scramble = [turn + direction]
    turns.append(turn)

    for turn_num in range(1, scram_len):
        direction = random.choice(directions)
        last_turn = turns[turn_num - 1]
        while turn == last_turn or (opp[turn] == last_turn and turns[turn_num - 2] == opp[last_turn]):
            turn = random.choice(faces)
        scramble.append(turn + direction)
        turns.append(turn)

    return " ".join(scramble)


if __name__ == "__main__":
    for i in range(100):
        print(gen_premove(3))

    # print(get_bld_scramble())
