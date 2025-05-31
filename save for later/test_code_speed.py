import random
import timeit

setup = """import random
import sys

moves = ["U", "D", "F", "B", "R", "L"]
dir = ["", "'", "2"]
slen = random.randint(25, 25)


def gen_scramble():
    # Make array of arrays that represent moves ex. U' = ['U', "'"]
    s = valid([[random.choice(moves), random.choice(dir)] for x in range(slen)])

    # Format scramble to a string with movecount
    return ''.join(str(s[x][0]) + str(s[x][1]) + ' ' for x in range(len(s))) + "[" + str(slen) + "]"


def valid(ar):
    # Check if Move behind or 2 behind is the same as the random move
    # this gets rid of 'R R2' or 'R L R2' or similar for all moves
    for x in range(1, len(ar)):
        while ar[x][0] == ar[x - 1][0]:
            ar[x][0] = random.choice(moves)
    for x in range(2, len(ar)):
        while ar[x][0] == ar[x - 2][0] or ar[x][0] == ar[x - 1][0]:
            ar[x][0] = random.choice(moves)
    return ar"""

a = timeit.timeit("gen_scramble()", number=1000000, setup=setup)

faces = ["U", "L", "F", "R", "B", "D"]
directions = ["", "'", "2"]

opp = {
    "U": "D",
    "D": "U",
    "F": "B",
    "B": "F",
    "L": "R",
    "R": "L",
}


def c():
    turns = []

    scram_len = random.randint(25, 25)

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

    return " ".join(scramble)


print(a)
b = timeit.timeit("gen_premove()", number=1000000, setup=setup)
print(b)
# 51.43338290000247
# 47.32705639999767
