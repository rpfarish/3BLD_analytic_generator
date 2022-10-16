"""Put your letter scheme here."""

# -------EDGES--------
# U Face
UB = 'A'
UR = 'B'
UF = 'U'
UL = 'D'

# L Face
LU = 'E'
LF = 'F'
LD = 'G'
LB = 'H'

# F Face
FU = 'K'
FR = 'J'
FD = 'I'
FL = 'L'

# R Face
RU = 'M'
RB = 'N'
RD = 'O'
RF = 'P'

# B Face
BU = 'Z'
BL = 'R'
BD = 'S'
BR = 'T'

# D Face
DF = 'C'
DR = 'V'
DB = 'W'
DL = 'X'

# -------CORNERS--------

# U Face
UBL = 'A'
UBR = 'B'
UFR = 'U'
UFL = 'D'

# L Face
LUB = 'J'
LUF = 'F'
LDF = 'G'
LDB = 'H'

# F Face
FUL = 'E'
FUR = 'I'
FDR = 'K'
FDL = 'L'

# R Face
RUF = 'X'
RUB = 'N'
RDB = 'O'
RDF = 'P'

# B Face
BUR = 'R'
BUL = 'M'
BDL = 'S'
BDR = 'T'

# D Face
DFL = 'C'
DFR = 'V'
DBR = 'W'
DBL = 'Z'

letter_scheme = dict(
    # U Face
    UB='A',
    UR='B',
    UF='U',
    UL='D',

    # L Face
    LU='E',
    LF='F',
    LD='G',
    LB='H',

    # F Face
    FU='K',
    FR='J',
    FD='I',
    FL='L',

    # R Face
    RU='M',
    RB='N',
    RD='O',
    RF='P',

    # B Face
    BU='Z',
    BL='R',
    BD='S',
    BR='T',

    # D Face
    DF='C',
    DR='V',
    DB='W',
    DL='X',

    # -------CORNERS--------

    # U Face
    UBL='A',
    UBR='B',
    UFR='U',
    UFL='D',

    # L Face
    LUB='J',
    LUF='F',
    LDF='G',
    LDB='H',

    # F Face
    FUL='E',
    FUR='I',
    FDR='K',
    FDL='L',

    # R Face
    RUF='X',
    RUB='N',
    RDB='O',
    RDF='P',

    # B Face
    BUR='R',
    BUL='M',
    BDL='S',
    BDR='T',

    # D Face
    DFL='C',
    DFR='V',
    DBR='W',
    DBL='Z',
)


# -----BUFFERS------
# EDGE_BUFFER = UF
# CORNER_BUFFER = UFR


class PieceId:
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name if name is not None else pos
        self.face = self.pos[0]
        self.type = 'c' if len(pos) == 3 else 'e'

    def __repr__(self):
        return f'{self.pos}: {self.name}'  # Type: {self.type}'

    def __str__(self):
        return self.name

    def __add__(self, other):
        return self.pos + other.pos


class LetterScheme:

    def __init__(self, ltr_scheme=None, use_default=False):
        if ltr_scheme is None:
            ltr_scheme = letter_scheme
        self.scheme = {}

        # initialize scheme to null so IDE won't flag as missing property
        self.UB = ''
        self.UR = ''
        self.UF = ''
        self.UL = ''
        self.LU = ''
        self.LF = ''
        self.LD = ''
        self.LB = ''
        self.FU = ''
        self.FR = ''
        self.FD = ''
        self.FL = ''
        self.RU = ''
        self.RB = ''
        self.RD = ''
        self.RF = ''
        self.BU = ''
        self.BL = ''
        self.BD = ''
        self.BR = ''
        self.DF = ''
        self.DR = ''
        self.DB = ''
        self.DL = ''
        self.UBL = ''
        self.UBR = ''
        self.UFR = ''
        self.UFL = ''
        self.LUB = ''
        self.LUF = ''
        self.LDF = ''
        self.LDB = ''
        self.FUL = ''
        self.FUR = ''
        self.FDR = ''
        self.FDL = ''
        self.RUF = ''
        self.RUB = ''
        self.RDB = ''
        self.RDF = ''
        self.BUR = ''
        self.BUL = ''
        self.BDL = ''
        self.BDR = ''
        self.DFL = ''
        self.DFR = ''
        self.DBR = ''
        self.DBL = ''

        for pos, name in ltr_scheme.items():
            if use_default is False:
                piece = PieceId(pos, name)
                setattr(self, pos, piece)
                self.scheme[pos] = piece
            else:
                piece = PieceId(pos, pos)
                setattr(self, pos, piece)
                self.scheme[pos] = piece

    def __repr__(self):
        return f'{[str(x) for x in self.scheme.values()]}'

    def __getitem__(self, key):
        return self.scheme[key].name

    def __setitem__(self, key, value):
        self.scheme[key] = value

    def get_corners(self):
        return [str(x) for x in self.scheme.values() if x.type == 'c']

    def get_edges(self):
        return [str(x) for x in self.scheme.values() if x.type == 'e']


if __name__ == '__main__':
    scheme = LetterScheme(use_default=False)
    from pprint import pprint

    pprint(scheme)
    # print(scheme.BD)
