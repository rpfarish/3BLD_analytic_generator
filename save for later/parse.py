import re
from functools import reduce

import get_scrambles


def get_turn_parameters(move, pattern, pattern2, pattern3):
    face_turn = re.search(pattern, move)

    if not face_turn:
        raise Exception

    face_turn = face_turn.group()

    quarter_turns = re.search(pattern2, move)
    quarter_turns = int(quarter_turns.group()) if quarter_turns else 1

    prime = re.search(pattern3, move)
    prime = -1 if prime else 1

    return face_turn, quarter_turns, prime


def invert(scramble):
    if not scramble:
        return ""
    pattern = r"[UDFBRLSMEudfbrl]([Ww]?)"
    pattern2 = r"\d+"
    pattern3 = r"\'"
    scramble = scramble.strip().split()
    inv_scram = []
    for move in reversed(scramble):
        if not move:
            continue

        face_turn, quarter_turns, is_prime = get_turn_parameters(
            move, pattern, pattern2, pattern3
        )
        inverse_turns = (4 - (quarter_turns * is_prime)) % 4
        if not inverse_turns:
            continue

        turn_map = {1: "", 2: "2", 3: "'"}

        inv_scram.append(face_turn + turn_map[inverse_turns])
    return " ".join(inv_scram)


if __name__ == "__main__":
    print(invert("R"))
    print(invert("R'"))
    print(invert("R2"))
    print(invert("R2'"))
    print(invert("R9'"))
    print(invert("R39"))
    print(invert("R41"))
    print(invert("F Rw"))
