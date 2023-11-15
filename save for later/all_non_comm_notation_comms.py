import json
from pprint import pprint

from Cube import Memo
from Cube.letterscheme import LetterScheme

all_rud_edge_comms = [
    "D' R' U' R U R U R U' R' U' D",
    "D' U R U R' U' R' U' R' U R D",
    "U' R' D' R D R D R D' R' U D'",
    "U' D R D R' D' R' D' R' D R U",
    "U R D R' D' R' D' R' D R D U'",
    "U R' D' R D R D R D' R' D' U'",
    "D' U R' D' R D R D R D' R' U'",
    "U D R D R' D' R' D' R' D R U'",
    "R D R' D' R' D' R' D R D",
    "D R D R' D' R' D' R' D R",
]
all_rud_edge_comms_eli = [
    "U' R' D' R D R D R D' R' U D'",
    "U' D R D R' D' R' D' R' D R U",
    "U' D R' U' R U R U R U' R' D'",
    "U R D R' D' R' D' R' D R D U'",
    "D' U R' D' R D R D R D' R' U'",
]

with open("../Settings/settings.json") as f:
    settings = json.loads(f.read())
    letterscheme_names = settings['letter_scheme']
    letterscheme = LetterScheme(ltr_scheme=letterscheme_names)

comms_to_print = []
for case in all_rud_edge_comms_eli:
    cube_names = Memo(case, ls=letterscheme)
    cube = Memo(case)
    cube_memo = cube.memo_edges()
    cube_memo_names = cube_names.translate_letter_scheme(cube_memo, translate_type="name")
    buffer = 'UF'

    if len(cube_memo) == 4:
        buffer = cube_memo[0]
        memo = cube_memo_names[1:-1]
        memo = cube.format_edge_memo(memo)
        print(f"{buffer} {memo[::-1]}: {case}")
        comms_to_print.append(f"{buffer} {memo[::-1]}: {case}")

    elif len(cube_memo) == 2:
        memo = cube.format_edge_memo(cube_memo_names)
        print(f"{buffer} {memo[::-1]}: {case}")
        comms_to_print.append(f"{buffer} {memo[::-1]}: {case}")

pprint(comms_to_print)
print(len(comms_to_print))

ru_and_rud_edge_comms = [
    "UF VD: R' U' R U R U R U' R' U'",
    "UF WD: D' R' U' R U R U R U' R' U' D",
    "UF VJ: U2 R U' R' U' R' U' R U R U'",
    "UF VT: R' U R U R U R' U' R' U'",
    "UF DV: U R U R' U' R' U' R' U R",
    "UF JV: U R' U' R' U R U R U R' U2",
    "UF TV: U R U R U' R' U' R' U' R",
    "UF DW: D' U R U R' U' R' U' R' U R D",
    "UF XW: U' R' D' R D R D R D' R' U D'",
    "UF WX: U' D R D R' D' R' D' R' D R U",
    "UB VJ: R U' R' U' R' U' R U R U",
    "UB VT: R U' R' U' R' U R U R U R2'",
    "UB XC: U R D R' D' R' D' R' D R D U'",
    "UB DV: U' R' U' R U R U R U' R'",
    "UB JV: U' R' U' R' U R U R U R'",
    "UB TV: R2 U' R' U' R' U' R U R U R'",
    "UB XW: U R' D' R D R D R D' R' D' U'",
    "UB CX: D' U R' D' R D R D R D' R' U'",
    "UB WX: U D R D R' D' R' D' R' D R U'",
    "UR XC: R D R' D' R' D' R' D R D",
    "UR WX: D R D R' D' R' D' R' D R",
    "UL VJ: U R U' R' U' R' U' R U R",
    "UL VT: U' R' U R U R U R' U' R'",
    "UL JV: R' U' R' U R U R U R' U'",
    "UL TV: R U R U' R' U' R' U' R U"
]
# 10
all_rud_edge_comms = [
    "UF WD: D' R' U' R U R U R U' R' U' D",
    "UF DW: D' U R U R' U' R' U' R' U R D",
    "UF XW: U' R' D' R D R D R D' R' U D'",
    "UF WX: U' D R D R' D' R' D' R' D R U",
    "UB XC: U R D R' D' R' D' R' D R D U'",
    "UB XW: U R' D' R D R D R D' R' D' U'",
    "UB CX: D' U R' D' R D R D R D' R' U'",
    "UB WX: U D R D R' D' R' D' R' D R U'",
    "UR XC: R D R' D' R' D' R' D R D",
    "UR WX: D R D R' D' R' D' R' D R"
]

all_rud_edge_comms = [
    "UF WD: D' R' U' R U R U R U' R' U' D",
    "UF DW: D' U R U R' U' R' U' R' U R D",
    "UF XW: U' R' D' R D R D R D' R' U D'",
    "UF WX: U' D R D R' D' R' D' R' D R U",
    "UB XC: U R D R' D' R' D' R' D R D U'",
    "UB XW: U R' D' R D R D R D' R' D' U'",
    "UB CX: D' U R' D' R D R D R D' R' U'",
    "UB WX: U D R D R' D' R' D' R' D R U'",
    "UR XC: R D R' D' R' D' R' D R D",
    "UR WX: D R D R' D' R' D' R' D R"
]
all_rud_edge_comms_eli = [
    "UF XW: U' R' D' R D R D R D' R' U D'",
    "UF WX: U' D R D R' D' R' D' R' D R U",
    "UB DC: U' D R' U' R U R U R U' R' D'",
    "UB XC: U R D R' D' R' D' R' D R D U'",
    "UB CX: D' U R' D' R D R D R D' R' U'"
]

all_rud_edge_comms_dict = {
    "UF WD": "D' R' U' R U R U R U' R' U' D",
    "UF DW": "D' U R U R' U' R' U' R' U R D",
    "UF XW": "U' R' D' R D R D R D' R' U D'",
    "UF WX": "U' D R D R' D' R' D' R' D R U",
    "UB XC": "U R D R' D' R' D' R' D R D U'",
    "UB XW": "U R' D' R D R D R D' R' D' U'",
    "UB WX": "U D R D R' D' R' D' R' D R U'",
    "UR XC": "R D R' D' R' D' R' D R D",
    "UR WX": "D R D R' D' R' D' R' D R",
    "UB DC": "U' D R' U' R U R U R U' R' D'",
    "UB CX": "D' U R' D' R D R D R D' R' U'"
}

print(len(all_rud_edge_comms_dict))
pprint(all_rud_edge_comms_dict)
for pair, comm in all_rud_edge_comms_dict.items():
    print(f'{pair}: {comm}')
