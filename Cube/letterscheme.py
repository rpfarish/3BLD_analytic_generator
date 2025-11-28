import json
from typing import Optional

# letter_scheme = dict(
#     # -------EDGES--------
#     # U Face
#     UB="A",
#     UR="B",
#     UF="U",
#     UL="D",
#     # L Face
#     LU="E",
#     LF="F",
#     LD="G",
#     LB="H",
#     # F Face
#     FU="K",
#     FR="J",
#     FD="I",
#     FL="L",
#     # R Face
#     RU="M",
#     RB="N",
#     RD="O",
#     RF="P",
#     # B Face
#     BU="Z",
#     BL="R",
#     BD="S",
#     BR="T",
#     # D Face
#     DF="C",
#     DR="V",
#     DB="W",
#     DL="X",
#     # -------CORNERS--------
#     # U Face
#     UBL="A",
#     UBR="B",
#     UFR="U",
#     UFL="D",
#     # L Face
#     LUB="J",
#     LUF="F",
#     LDF="G",
#     LDB="H",
#     # F Face
#     FUL="E",
#     FUR="I",
#     FDR="K",
#     FDL="L",
#     # R Face
#     RUF="X",
#     RUB="N",
#     RDB="O",
#     RDF="P",
#     # B Face
#     BUR="R",
#     BUL="M",
#     BDL="S",
#     BDR="T",
#     # D Face
#     DFL="C",
#     DFR="V",
#     DBR="W",
#     DBL="Z",
# )
#
#


class PieceId:
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name if name is not None else pos
        self.face = self.pos[0]
        self.type = "c" if len(pos) == 3 else "e"

    def __repr__(self):
        return f"'PieceId: {self.pos} => {self.name}'"  # Type: {self.type}'

    def __str__(self):
        return self.name

    def __add__(self, other):
        return self.pos + other.pos


class LetterScheme:
    def __init__(self, ltr_scheme: Optional[dict[str, str]] = None, use_default=False):
        self.is_default = use_default
        if ltr_scheme is None:
            with open("settings.json") as f:
                settings = json.loads(f.read())
                ltr_scheme = settings["letter_scheme"]
            if ltr_scheme is None:
                raise ValueError("letter_scheme not found in settings.json")

        if len(ltr_scheme) != 48:
            raise ValueError(
                f"Letter scheme must contain exactly 48 letter entries, got {len(ltr_scheme)}"
            )

        self.scheme = {}
        self.reverse_scheme_corners = {}
        self.reverse_scheme_edges = {}

        # initialize scheme to null so IDE won't flag as missing property
        self.UB = ""
        self.UR = ""
        self.UF = ""
        self.UL = ""
        self.LU = ""
        self.LF = ""
        self.LD = ""
        self.LB = ""
        self.FU = ""
        self.FR = ""
        self.FD = ""
        self.FL = ""
        self.RU = ""
        self.RB = ""
        self.RD = ""
        self.RF = ""
        self.BU = ""
        self.BL = ""
        self.BD = ""
        self.BR = ""
        self.DF = ""
        self.DR = ""
        self.DB = ""
        self.DL = ""
        self.UBL = ""
        self.UBR = ""
        self.UFR = ""
        self.UFL = ""
        self.LUB = ""
        self.LUF = ""
        self.LDF = ""
        self.LDB = ""
        self.FUL = ""
        self.FUR = ""
        self.FDR = ""
        self.FDL = ""
        self.RUF = ""
        self.RUB = ""
        self.RDB = ""
        self.RDF = ""
        self.BUR = ""
        self.BUL = ""
        self.BDL = ""
        self.BDR = ""
        self.DFL = ""
        self.DFR = ""
        self.DBR = ""
        self.DBL = ""

        for pos, name in ltr_scheme.items():
            if use_default is False:
                piece = PieceId(pos, name)
                setattr(self, pos, piece)
                self.scheme[pos] = piece
                self._add_reverse_scheme(pos, name)
            else:
                piece = PieceId(pos, pos)
                setattr(self, pos, piece)
                self.scheme[pos] = piece
                self._add_reverse_scheme(pos, pos)

    def _add_reverse_scheme(self, pos, name):
        if self.scheme[pos].type == "c":
            self.reverse_scheme_corners[name] = pos
        if self.scheme[pos].type == "e":
            self.reverse_scheme_edges[name] = pos

    def convert_to_pos(self, buffer, piece, piece_type=None) -> str:
        if self.scheme.get(piece) is not None:
            return piece
        elif self.scheme[buffer].type == "c" or piece_type == "corner":
            return self.reverse_scheme_corners[piece]
        elif self.scheme[buffer].type == "e" or piece_type == "edge":
            return self.reverse_scheme_edges[piece]
        raise ValueError(f"piece '{piece}' or piece_type '{piece_type}' is not valid")

    def convert_to_pos_from_type(self, piece, piece_type) -> str:
        if self.scheme.get(piece) is not None:
            return piece
        elif piece_type == "corner":
            return self.reverse_scheme_corners[piece]
        elif piece_type == "edge":
            return self.reverse_scheme_edges[piece]
        raise ValueError(f"piece '{piece}' or piece_type '{piece_type}' is not valid")

    def convert_pair_to_pos(self, buffer, pair) -> tuple[str, str]:
        a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
        return self.convert_to_pos(buffer, a), self.convert_to_pos(buffer, b)

    def convert_pair_to_pos_type(self, pair, piece_type) -> tuple[str, str]:
        a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
        return self.convert_to_pos_from_type(
            a, piece_type
        ), self.convert_to_pos_from_type(b, piece_type)

    def __repr__(self):
        return str({str(pos): letter for pos, letter in self.scheme.items()})

    def __getitem__(self, key):
        return self.scheme[key].name

    def __setitem__(self, key, value):
        self.scheme[key] = value

    def get_corners(self):
        return [str(x) for x in self.scheme.values() if x.type == "c"]

    def get_edges(self):
        return [str(x) for x in self.scheme.values() if x.type == "e"]

    def get_all_dict(self):
        return {str(pos): str(letter) for pos, letter in self.scheme.items()}


def convert_letterpairs(
    to_convert,
    direction,
    letter_scheme,
    piece_type=None,
    display=False,
    return_type="set",
):
    """
    Convert letter pairs using a LetterScheme object.

    Args:
        to_convert: List/set of letter pairs to convert
        direction: 'letter_to_loc' or 'loc_to_letter'
        letter_scheme: LetterScheme object to use for conversions
        piece_type: 'corners' or 'edges' (required for letter_to_loc direction)
        display: Whether to print converted pairs
        return_type: 'set' or 'list' for return format
    """
    if direction == "letter_to_loc" and piece_type is None:
        raise Exception("Cannot convert from letter to location without piece type")

    if piece_type is not None and piece_type not in ("corners", "edges"):
        raise ValueError(
            f"Value for 'piece_type' should be either 'corners' or 'edges', not '{piece_type}'"
        )

    converted_set = set()
    converted_list = []
    for pair in to_convert:
        # Split the pair in half
        a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
        converted_a, converted_b = "", ""

        if direction == "loc_to_letter":
            # Convert location to letter using the scheme
            # Uses __getitem__ to get letter name
            converted_a = letter_scheme[a]
            converted_b = letter_scheme[b]
            converted_pair = f"{converted_a}{converted_b}"

        elif direction == "letter_to_loc":
            # Convert letter to location using the appropriate piece type
            if piece_type == "corners":
                converted_a = letter_scheme.convert_to_pos_from_type(a, "corner")
                converted_b = letter_scheme.convert_to_pos_from_type(b, "corner")
            elif piece_type == "edges":
                converted_a = letter_scheme.convert_to_pos_from_type(a, "edge")
                converted_b = letter_scheme.convert_to_pos_from_type(b, "edge")
            converted_pair = f"{converted_a}{converted_b}"

        else:
            raise ValueError(
                f"Invalid direction '{direction}'. Must be 'loc_to_letter' or 'letter_to_loc'"
            )

        if not converted_a or not converted_b:
            print(f"{letter_scheme=}, {piece_type=}, {pair=}")
            raise ValueError("Converted a and converted b must be nonempty")

        if display:
            print(f"'{converted_pair}',")

        converted_set.add(converted_pair)
        converted_list.append(converted_pair)

    if return_type == "set":
        return converted_set
    elif return_type == "list":
        return converted_list
    else:
        raise ValueError(
            f"Invalid return_type '{return_type}'. Must be 'set' or 'list'"
        )


if __name__ == "__main__":
    scheme = LetterScheme()
    converted = scheme.convert_to_pos_from_type("N", "edge")
    print(converted)
