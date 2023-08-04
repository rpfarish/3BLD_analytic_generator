"""Put your letter scheme here."""

# # -------EDGES--------
# # U Face
# UB = 'A'
# UR = 'B'
# UF = 'U'
# UL = 'D'
#
# # L Face
# LU = 'E'
# LF = 'F'
# LD = 'G'
# LB = 'H'
#
# # F Face
# FU = 'K'
# FR = 'J'
# FD = 'I'
# FL = 'L'
#
# # R Face
# RU = 'M'
# RB = 'N'
# RD = 'O'
# RF = 'P'
#
# # B Face
# BU = 'Z'
# BL = 'R'
# BD = 'S'
# BR = 'T'
#
# # D Face
# DF = 'C'
# DR = 'V'
# DB = 'W'
# DL = 'X'
#
# # -------CORNERS--------
#
# # U Face
# UBL = 'A'
# UBR = 'B'
# UFR = 'U'
# UFL = 'D'
#
# # L Face
# LUB = 'J'
# LUF = 'F'
# LDF = 'G'
# LDB = 'H'
#
# # F Face
# FUL = 'E'
# FUR = 'I'
# FDR = 'K'
# FDL = 'L'
#
# # R Face
# RUF = 'X'
# RUB = 'N'
# RDB = 'O'
# RDF = 'P'
#
# # B Face
# BUR = 'R'
# BUL = 'M'
# BDL = 'S'
# BDR = 'T'
#
# # D Face
# DFL = 'C'
# DFR = 'V'
# DBR = 'W'
# DBL = 'Z'

letter_scheme = dict(
    # -------EDGES--------

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

# todo this should be using settings.json
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

    def __init__(self, ltr_scheme: dict[str: str] = None, use_default=False):
        self.is_default = use_default
        if ltr_scheme is None:
            ltr_scheme = letter_scheme
        self.scheme = {}
        self.reverse_scheme_corners = {}
        self.reverse_scheme_edges = {}

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
                self._add_reverse_scheme(pos, name)
            else:
                piece = PieceId(pos, pos)
                setattr(self, pos, piece)
                self.scheme[pos] = piece
                self._add_reverse_scheme(pos, pos)

    def _add_reverse_scheme(self, pos, name):
        if self.scheme[pos].type == 'c':
            self.reverse_scheme_corners[name] = pos
        if self.scheme[pos].type == 'e':
            self.reverse_scheme_edges[name] = pos

    def convert_to_pos(self, buffer, piece):
        if self.scheme.get(piece) is not None:
            return piece
        elif self.scheme[buffer].type == 'c':
            return self.reverse_scheme_corners[piece]
        elif self.scheme[buffer].type == 'e':
            return self.reverse_scheme_edges[piece]

    def convert_pair_to_pos(self, buffer, pair):
        a, b = pair[:len(pair) // 2], pair[len(pair) // 2:]
        return self.convert_to_pos(buffer, a), self.convert_to_pos(buffer, b)

    def __repr__(self):
        return str({str(pos): letter for pos, letter in self.scheme.items()})

    def __getitem__(self, key):
        return self.scheme[key].name

    def __setitem__(self, key, value):
        self.scheme[key] = value

    def get_corners(self):
        return [str(x) for x in self.scheme.values() if x.type == 'c']

    def get_edges(self):
        return [str(x) for x in self.scheme.values() if x.type == 'e']

    def get_all_dict(self):
        return {str(pos): str(letter) for pos, letter in self.scheme.items()}


def convert_letterpairs(to_convert, direction, piece_type=None, display=False, return_type='set'):
    """
    :piece_type corner, edge
    :direction letter_to_loc, loc_to_letter letter representation and location
    """
    # todo setting for letter scheme modular and global
    # add letterscheme as a param
    if direction == "letter_to_loc" and piece_type is None:
        raise Exception("Cannot convert letter scheme from letter to name without piece type")

    if piece_type not in ("corners", "edges",):
        raise ValueError(f"Value for 'piece_type' should be either corners or edges not '{piece_type}'")

    convert_table = dict(
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
    corner_letter_to_loc = dict(
        A='UBL',
        B='UBR',
        U='UFR',
        D='UFL',
        J='LUB',
        F='LUF',
        G='LDF',
        H='LDB',
        E='FUL',
        I='FUR',
        K='FDR',
        L='FDL',
        X='RUF',
        N='RUB',
        O='RDB',
        P='RDF',
        R='BUR',
        M='BUL',
        S='BDL',
        T='BDR',
        C='DFL',
        V='DFR',
        W='DBR',
        Z='DBL',

    )

    edge_letter_to_loc = dict(
        A='UB',
        B='UR',
        U='UF',
        D='UL',
        E='LU',
        F='LF',
        G='LD',
        H='LB',
        K='FU',
        J='FR',
        I='FD',
        L='FL',
        M='RU',
        N='RB',
        O='RD',
        P='RF',
        Z='BU',
        R='BL',
        S='BD',
        T='BR',
        C='DF',
        V='DR',
        W='DB',
        X='DL',
    )

    if piece_type == "corners":
        convert_table |= corner_letter_to_loc
    elif piece_type == "edges":
        convert_table |= edge_letter_to_loc

    # for i, j in s.items():
    #     print(f"{j} = '{i}',")

    converted_set = set()
    converted_list = []
    for i in to_convert:
        a, b = i[:len(i) // 2], i[len(i) // 2:]
        if display:
            print(f"'{convert_table[a]}{convert_table[b]}',")
        converted_set.add(f"{convert_table[a]}{convert_table[b]}")
        converted_list.append(f"{convert_table[a]}{convert_table[b]}")
    if return_type == 'set':
        return converted_set
    elif return_type == 'list':
        return converted_list


if __name__ == '__main__':
    scheme = LetterScheme(use_default=False)
    # from pprint import pprint
    #
    # pprint(scheme)

    # print(scheme.BD)

    # convert_letterpairs(["SF", "ND", "OP", "ZF", "SI", "LJ", "TF", "XP", "AR", "MG",
    #             "ZB", "PD", "LG", "BP", "GH", "AI", "MX", "PR", "GZ", "DL"])
    # print(convert_letterpairs(
    #     ["TF", "XP", "PD", "LG", "BP", "AI", "GZ", "DL", "CG", "DF", "LT", "SO", "SV", "TP", "HG", "FR", "GL", "ZX",
    #      "OJ", "XV", "AS", "JV", "NX", "VW", "RP", "OG", "ZM", "LP", "XS", "CB", "SR", "GW", "IZ", "PS", "DB", "NJ",
    #      "CZ", "FW", ], direction="letter_to_loc", piece_type='edges',
    # ))
    # #
    # fg = {'BUDL', 'BRRF', 'LDFL', 'DLBD', 'BDBL', 'FDBU', 'RBFR', 'URRF', 'LBLD', 'BDRD', 'LDBU', 'DFLD', 'BRLF',
    #       'LFDB', 'BLRF', 'ULLF', 'UBFD', 'ULUR', 'FRDR', 'BURU', 'RFUL', 'RDFR', 'FLBR', 'FLRF', 'ULFL', 'LDDB',
    #       'DRDB', 'FLLD', 'UBBD', 'RBDL', 'DLDR', 'DFUR', 'BDDR', 'DLRF', 'RFBD', 'LFBL', 'RDLD', 'DFBU'}
    #
    # print(convert_letterpairs(fg, direction='loc_to_letter', piece_type='edges') == set(
    #     ["TF", "XP", "PD", "LG", "BP", "AI", "GZ", "DL", "CG", "DF", "LT", "SO", "SV", "TP", "HG", "FR", "GL", "ZX",
    #      "OJ", "XV", "AS", "JV", "NX", "VW", "RP", "OG", "ZM", "LP", "XS", "CB", "SR", "GW", "IZ", "PS", "DB", "NJ",
    #      "CZ", "FW", ]), )
    print(convert_letterpairs(
        {'LUFDFL', 'FULFDR', 'UBRRDF', 'FDLRDB', 'FDLUFL', 'RUBBDR', 'BURDFL', 'LDFUBL', 'RUBFDR', 'BDRBUL', 'UFLLUB',
         'LDBDBR', 'BULDFR', 'UBLBDL', 'DBRRUB', 'BURDBR', 'FDRFUL', 'DBLBUL', 'DFLRDF', 'FULDFR', 'BULFUL', 'RDBRDF',
         'BDLUFL', 'RDBUBR', 'RUBDFR', 'LDFRUB', 'LDFUBR', 'DBLLUF', 'DBRDFR', 'LDBFUL', 'LUFBUL', 'LDBBDR', 'BURBDR',
         'UFLDBL', 'LDFLUF', 'FDRFDL', 'FDRBDR', 'RDBLUF', 'FDLLUF', 'FDLDBR', 'FULBDR', 'DFLUBR', 'DFRLDF', 'DFLBDR',
         'LUBFUL', 'LUBRDF', 'LDFFUL', 'FULUBL', 'DBRUFL', 'BURFDR', 'BDRRUB', 'FULRDB', 'UFLDFL', 'UBLBUR', 'RUBLDF',
         'RDBUBL', 'BDRFDL', 'DFRBDL', 'BDRDFL', 'DFLBUR', 'LDFBDL', 'BDRRDF', 'LUBRDB', 'LDBBUR', 'RUBFDL', 'BULLDF',
         'LDBFDR', 'BULRDB', 'LDBUBL', 'FULDBL', 'UBLRUB', 'DFRUBR', 'LUBFDR', 'BURDBL', 'UBRUBL', 'BULBUR', 'RDFDBR',
         'RDFBUR', 'RDBBUL', 'FDRUBL', 'UBRBUL', 'FDRBUL', 'RDFBUL', 'DFRFUL', 'LUFBDR', 'FDRRDB', 'UBLFUL', 'RDBUFL',
         'DFLLDB', 'UFLDFR', 'DFLUBL', 'BDLBUR', 'BULDBL', 'DBLRDF', 'LUFBDL', 'BULUBR', 'FDRLUF', 'FDRRUB', 'BDRLUB',
         'LDBBUL', 'RDFDBL', 'BDLLUF', 'BDLDFR', 'LDBRDB', 'DBLUFL', 'DFRBUR', 'LDBDFL', 'UFLBDL', 'DFRLUB', 'DFRBUL',
         'BDLBUL', 'LDFLUB', 'LDBFDL', 'DFLDBR', 'DBLDFL', 'LUBDBR', 'DBRLDF', 'RDFFUL', 'LDFFDR', 'DBRFDL', 'UBRLUB',
         'DBRUBR', 'DBLFUL', 'LDFLDB', 'LUFRUB', 'BULLDB', 'DFRRDB', 'RDFBDL', 'RUBLUB', 'UBLRDB', 'FDRLUB', 'DFRFDL',
         'UBRDFL', 'RUBFUL', 'BDLDBR', 'DBRRDF', 'DFLRDB', 'RDFUBL', 'LDFBUL', 'BDRBDL', 'RUBUFL', 'LUBBUR', 'LUBDBL',
         'UBRFDL', 'BULFDR', 'LDFRDB', 'FDRDBL', 'FULBDL', 'LUFUBL', 'RDBLDF', 'UBLUFL', 'DFLLUB', 'LUFLUB', 'RDBDFR',
         'DBRLUB', 'LUBDFL', 'FULDBR', 'RDFBDR', 'DBRFUL', 'UFLUBL', 'BDRLDF', 'UBRLDF', 'UBRDBR', 'LDBRUB', 'BURFDL',
         'FULBUL', 'UFLFDL', 'BDRFDR', 'BURFUL', 'FDLFDR', 'LUBUBR', 'RDFLUB', 'RDFLDB', 'DBRDBL', 'LDBDFR', 'LUBRUB',
         'FDLBUL', 'UBLDBR', 'BURUBL', 'DFRLUF', 'BDRFUL', 'LDFDBL', 'UFLDBR', 'BULRUB', 'DFRDBL', 'DBLDFR', 'UBLLDB',
         'BDLUBR', 'RDFRDB', 'DBRLDB', 'DBRDFL', 'BDRUBL', 'BURLUF', 'DFRRUB', 'LUFFDR', 'FDLDBL', 'UBRDFR', 'BURLDF',
         'FULRUB', 'LUFRDB', 'RUBLDB', 'FULBUR', 'DFLDFR', 'LUFBUR', 'BDRLDB', 'UBLDBL', 'LDBUBR', 'FDRLDF', 'BULDBR',
         'LDFRDF', 'UBRLDB', 'DFRLDB', 'FULFDL', 'FDLBDL', 'RDBFDL', 'RUBDBR', 'UBRLUF', 'RDBBUR', 'BDRUFL', 'BDLRUB',
         'FDLLUB', 'DFLLUF', 'UBRDBL', 'FDRUBR', 'RDBDBL', 'LDBLUB', 'FDRBUR', 'UBRRDB', 'BURUFL', 'LUFLDF', 'LDBRDF',
         'FDRDFL', 'UBLFDL', 'FDLUBR', 'UBRBDL', 'DBLLDF', 'FDLRDF', 'DBRFDR', 'RDBLUB', 'DFLDBL', 'FULRDF', 'LUFDBR',
         'LUBDFR', 'LDBLDF', 'BURBDL', 'UFLLDF', 'UBLUBR', 'DBRBUL', 'FDRUFL', 'FULUBR', 'DBLUBR', 'DFLFUL', 'UFLRUB',
         'UFLLDB', 'RDBBDL', 'DFRUFL', 'FDLDFR', 'FULLDB', 'FULLUB', 'UFLBUL', 'LDBLUF', 'FDLLDB', 'DBLUBL', 'FDRLDB',
         'BURRDB', 'DBLRUB', 'DBRUBL', 'BDLFDL', 'DBLBUR', 'LDFDBR', 'RUBBDL', 'DFLUFL', 'UBLLDF', 'UFLUBR', 'DBLLUB',
         'RDBFUL', 'RUBUBL', 'LUBLDB', 'FDLRUB', 'RDFRUB', 'RDBDFL', 'DFRDFL', 'LDFDFR', 'DFRUBL', 'BDLRDF', 'DBLDBR',
         'BDLDFL', 'LUFRDF', 'BDLRDB', 'RUBRDF', 'UBLDFL', 'LDFUFL', 'LUBBDL', 'RDFDFL', 'RDBLDB', 'LUFDFR', 'FDLFUL',
         'LUFUBR', 'BURRDF', 'BULDFL', 'FDRBDL', 'UBRUFL', 'BDLFUL', 'DFRDBR', 'FDRDBR', 'RDFFDL', 'RDBRUB', 'UBLRDF',
         'LUBFDL', 'BDRBUR', 'UFLBDR', 'RUBDFL', 'DBLFDR', 'BULLUF', 'FDLBDR', 'RDFLUF', 'RDFLDF', 'UBLFDR', 'UFLRDB',
         'BULBDR', 'BDLLDF', 'DFLBUL', 'UBLLUF', 'UBRFUL', 'RDFUBR', 'LUFLDB', 'DBRBDL', 'LUBLDF', 'DBLBDR', 'FDLUBL',
         'FULLDF', 'UBLBDR', 'BULUFL', 'BULFDL', 'DFLRUB', 'BURLUB', 'DBRLUF', 'FDLBUR', 'RUBLUF', 'DBLFDL', 'BURDFR',
         'UFLRDF', 'LDFBDR', 'FULDFL', 'RDFUFL', 'BURLDB', 'BULRDF', 'BDLLUB', 'RUBDBL', 'UBRBDR', 'LUBLUF', 'RUBRDB',
         'DFRBDR', 'RUBBUL', 'UFLFDR', 'BDLFDR', 'LUFDBL', 'LUBBDR', 'DFLBDL', 'DBRBUR', 'LUBUFL', 'UFLBUR', 'BDLBDR',
         'DFLFDR', 'BDRDFR', 'LDFBUR', 'BDRDBL', 'BDRUBR', 'BULBDL', 'RDBFDR', 'DBLRDB', 'UBRFDR', 'LUFFDL', 'BURBUL',
         'LDBUFL', 'UBLDFR', 'BDLUBL', 'BDRLUF'},
        'loc_to_letter', 'corners'))
    print(scheme.convert_pair_to_pos("UB", "DF"))
