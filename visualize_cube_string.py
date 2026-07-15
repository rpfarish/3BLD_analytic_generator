import kociemba

BG = {
    "U": "\033[30;48;5;255m",  # White
    "R": "\033[97;48;5;124m",  # Dark Red
    "F": "\033[97;48;5;22m",  # Dark Green
    "D": "\033[30;48;5;220m",  # Gold
    "L": "\033[30;48;5;166m",  # Dark Orange
    "B": "\033[97;48;5;19m",  # Dark Blue
}
RESET = "\033[0m"

EDGE_COLORS = {
    0: ("U", "F"),
    1: ("U", "B"),
    2: ("U", "R"),
    3: ("U", "L"),
    4: ("D", "F"),
    5: ("D", "R"),
    6: ("D", "B"),
    7: ("D", "L"),
    8: ("F", "R"),
    9: ("F", "L"),
    10: ("B", "L"),
    11: ("B", "R"),
}


def edges_to_facelet_string(perm, ori):
    """
    perm[pos] = edge cubie at position pos
    ori[pos] = 0 (oriented) or 1 (flipped)

    Edge numbering:
        0 UF
        1 UB
        2 UR
        3 UL
        4 DF
        5 DR
        6 DB
        7 DL
        8 FR
        9 FL
       10 BL
       11 BR
    """

    facelets = (
        {f"U{i}": "U" for i in range(1, 10)}
        | {f"R{i}": "R" for i in range(1, 10)}
        | {f"F{i}": "F" for i in range(1, 10)}
        | {f"D{i}": "D" for i in range(1, 10)}
        | {f"L{i}": "L" for i in range(1, 10)}
        | {f"B{i}": "B" for i in range(1, 10)}
    )

    edge_facelets = {
        0: ("U8", "F2"),
        1: ("U2", "B2"),
        2: ("U6", "R2"),
        3: ("U4", "L2"),
        4: ("D2", "F8"),
        5: ("D6", "R8"),
        6: ("D8", "B8"),
        7: ("D4", "L8"),
        8: ("F6", "R4"),
        9: ("F4", "L6"),
        10: ("B6", "L4"),
        11: ("B4", "R6"),
    }

    edge_colors = EDGE_COLORS

    for pos in range(12):
        cubie = perm[pos]
        colors = list(edge_colors[cubie])

        if ori[pos]:
            colors.reverse()

        f1, f2 = edge_facelets[pos]
        facelets[f1] = colors[0]
        facelets[f2] = colors[1]

    order = (
        [f"U{i}" for i in range(1, 10)]
        + [f"R{i}" for i in range(1, 10)]
        + [f"F{i}" for i in range(1, 10)]
        + [f"D{i}" for i in range(1, 10)]
        + [f"L{i}" for i in range(1, 10)]
        + [f"B{i}" for i in range(1, 10)]
    )

    return "".join(facelets[f] for f in order)


def sticker(c):
    return f"{BG[c]} {c} {RESET}"


def visualize_cube(cube):
    """
    cube: 54-character Kociemba facelet string in URFDLB face order.
    """

    if len(cube) != 54:
        raise ValueError("Cube string must have length 54.")

    faces = {
        "U": cube[0:9],
        "R": cube[9:18],
        "F": cube[18:27],
        "D": cube[27:36],
        "L": cube[36:45],
        "B": cube[45:54],
    }

    def row(face, r):
        return "".join(sticker(x) for x in faces[face][3 * r : 3 * r + 3])

    pad = " " * 12

    print("\nUp")
    for r in range(3):
        print(pad + row("U", r))

    print("\nLeft              Front             Right             Back")
    for r in range(3):
        print(
            row("L", r)
            + "   "
            + row("F", r)
            + "   "
            + row("R", r)
            + "   "
            + row("B", r)
        )

    print("\nDown")
    for r in range(3):
        print(pad + row("D", r))


if __name__ == "__main__":
    cube = "URUUUDUBURFRRRDRURFLFFFFFUFDRDBDFDUDLLLBLLLRLBDBDBLBBB"
    cube = "UFUUULURURDRBRRRRRFDFUFLFBFDDDFDFDFDLBLBLLLDLBLBRBUBUB"

    perm = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ori = [1] * 12  # [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cube = edges_to_facelet_string(perm, ori)
    solved = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    visualize_cube(cube)

    print("Facelet string", cube)
    scram = kociemba.solve(cube)
    print(scram)

    """
    U face
    UBULURUFU
   
    R face
    RURFRBRDR

    F face
    FUFLFRFDF
    
    D face
    DFDLDRDBD

    L face
    LULBLFLDL
    
    B face
    BUBLBRBDB
    """
