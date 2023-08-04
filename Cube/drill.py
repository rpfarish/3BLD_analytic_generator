import itertools
import json
import random
import time

import get_scrambles
from Cube import Cube
from Cube.letterscheme import LetterScheme, convert_letterpairs
from Cube.memo import Memo
from max_comms import MAX_COMMS


class Drill:

    def __init__(self, memo: Memo = None):
        if memo is not None:
            self.cube_memo: Memo = memo
        else:
            self.cube_memo: Memo = Memo()

        self.max_cycles_per_buffer = {buffer: (8 - i) // 2 for i, buffer in
                                      enumerate(self.cube_memo.corner_buffer_order, 1)}
        self.max_cycles_per_buffer |= {buffer: (12 - i) // 2 for i, buffer in
                                       enumerate(self.cube_memo.edge_buffer_order, 1)}

        self.total_cases_per_buffer = {
            'UFR': 378, 'UBR': 270, 'UBL': 180, 'UFL': 108, 'RDF': 54, 'RDB': 18,
            'UF': 440, 'UB': 360, 'UR': 288, 'UL': 224, 'DF': 168, 'DB': 120, 'FR': 80, 'FL': 48, 'DR': 24, 'DL': 8
        }

    # memo
    def generate_drill_list(self, piece_type, ltr_scheme: LetterScheme, buffer, target):
        # pick what letter scheme to use
        # how to separate c from e
        # just doing corners first
        all_targets = ltr_scheme.get_corners()
        self.remove_piece(all_targets, buffer, ltr_scheme)

        # random_list = []
        # # generate random pair
        # for _ in range(18):
        #     target_list = all_targets[:]
        #     random_list.append(generate_random_pair(target_list, ltr_scheme))

        target_list = all_targets[:]
        # remove buffer stickers
        self.remove_piece(target_list, target, ltr_scheme)

        # generate random pairs
        # generate specific pairs
        # generate target groups e.g. just Z or H and k
        # generate inverse target groups
        # specify buffer
        return {target + i for i in target_list}

    # memo
    def get_target_scramble(self, algs_to_drill):
        # print("getting scramble", getting_scramble_depth)
        scramble = get_scrambles.get_scramble()

        cube = Cube(scramble, ls=self.ls)
        corner_memo = cube.format_corner_memo(cube.memo_corners()).split(' ')
        no_cycle_break_corner_memo = set()

        # if just the first target of the memo is the target eg: L then cycle break, this is bad

        corner_buffers = cube.corner_memo_buffers
        for pair in corner_memo:
            if len(pair) == 4 or len(pair) == 2:
                pair_len_half = len(pair) // 2
                a = pair[:pair_len_half]
                b = pair[pair_len_half:]
                # print(pair, pair_len_half, a, b)
            else:
                a = pair
                b = ''
            if a in corner_buffers or b in corner_buffers:
                break
            no_cycle_break_corner_memo.add(pair)

        alg_to_drill = algs_to_drill.intersection(no_cycle_break_corner_memo)

        # if all are same value inc count by 2
        # determine if max min deviation is more than ±1
        # find max
        # find min
        # find difference

        if algs_to_drill.intersection(no_cycle_break_corner_memo):
            return scramble, alg_to_drill.pop()
        else:
            return self.get_target_scramble(algs_to_drill)

    # print(max(alg_freq_dist.values()),  min(alg_freq_dist.values()), max(alg_freq_dist.values())-min(alg_freq_dist.values()))

    # memo
    def drill_corner_sticker(self, sticker_to_drill, single_cycle=True, return_list=False,
                             cycles_to_exclude: set = None):
        # from solution import Solution
        #
        # # todo support starting from any buffer
        # # support default certain alternate pseudo edge swaps depending on last corner target
        # scrambles = []
        #
        # all_corners = self.default_corners.copy()
        # buffer = self.default_corner_buffer
        # buffer_adj1, buffer_adj2 = self.adj_corners[buffer]
        # all_corners.remove(buffer)
        # all_corners.remove(buffer_adj1)
        # all_corners.remove(buffer_adj2)
        #
        # adj1, adj2 = self.adj_corners[sticker_to_drill]
        # all_corners.remove(sticker_to_drill)
        # all_corners.remove(adj1)
        # all_corners.remove(adj2)
        # algs_to_drill = {sticker_to_drill + i for i in all_corners}
        # number = 0
        #
        # if cycles_to_exclude is not None:
        #     algs_to_drill = algs_to_drill.difference(cycles_to_exclude)
        #
        # if single_cycle:
        #     frequency = 1
        # else:
        #     frequency = int(input("Enter freq (recommended less than 3): "))
        #
        # no_repeat = True
        # # I don't recommend going above 2 else it will take forever
        # while len(algs_to_drill) >= frequency:
        #     scramble = get_scrambles.gen_premove(28, min_len=25)
        #     cube = Cube(scramble, can_parity_swap=True, ls=self.ls)
        #     corner_memo = cube.format_corner_memo(cube.memo_corners()).split(' ')
        #     no_cycle_break_corner_memo = set()
        #     last_added_pair = ''
        #     corner_buffers = cube.corner_memo_buffers
        #     for pair in corner_memo:
        #         if len(pair) > 3:
        #             pair_len_half = len(pair) // 2
        #             a = pair[:pair_len_half]
        #             b = pair[pair_len_half:]
        #         elif not cycles_to_exclude:
        #             a = pair
        #             b = ''
        #         else:
        #             break
        #
        #         if a in corner_buffers or b in corner_buffers:
        #             break
        #         no_cycle_break_corner_memo.add(pair)
        #
        #     algs_in_scramble = algs_to_drill.intersection(no_cycle_break_corner_memo)
        #
        #     if len(algs_in_scramble) >= frequency:
        #         if not return_list:
        #             print("Scramble:", self.reduce_scramble(scramble))
        #             # todo make it so if you're no_repeat then allow to repeat the letter pairs
        #             response = input('Enter "r" to repeat letter pairs: ')
        #             if response == 'm':
        #                 Solution(scramble).display()
        #                 scrambles.append(scramble)
        #                 response = input('Enter "r" to repeat letter pair(s): ')
        #
        #             if response != 'r' and no_repeat:
        #                 algs_to_drill = algs_to_drill.difference(algs_in_scramble)
        #             print()
        #         else:
        #             algs_to_drill = algs_to_drill.difference(algs_in_scramble)
        #         scrambles.append(scramble)
        #
        # if return_list:
        #     return scrambles
        # todo fix buffer thing
        algs_to_drill = self.generate_drill_list('c', self.ls, self.default_corner_buffer, sticker_to_drill)

        alg_freq_dist = {str(pair): 0 for pair in algs_to_drill}
        # print(type(alg_freq_dist))
        # print('Running...')
        count = 2
        inc_amt = 2
        while True:
            scramble, alg_to_drill = self.get_target_scramble(algs_to_drill)
            # check if freq is < count and if so continue
            if alg_freq_dist[alg_to_drill] < count:
                alg_freq_dist[alg_to_drill] += 1
            elif len(set(alg_freq_dist.values())) == 1:
                print("Increasing count")
                count += inc_amt
            else:
                continue
            # print(alg_to_drill)
            # print(alg_freq_dist, sep="")
            # print(corner_memo)
            # print(no_cycle_break_corner_memo)
            # print("reducing scramble")
            print(scramble, end="")
            # print(self.reduce_scramble(scramble))
            input()

    # memo
    def drill_edge_buffer(self, edge_buffer: str, exclude_from_memo=None, return_list=False, translate_memo=False,
                          drill_set: set | None = None):
        # todo add edge flips hahaha

        scrams = {}
        total_cases = self.total_cases_per_buffer[edge_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[edge_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        edges = self.cube_memo.remove_irrelevant_edge_buffers(self.cube_memo.adj_edges, edge_buffer)

        all_edges = set(i + j for i, j in itertools.permutations(edges, 2) if
                        i != self.cube_memo.adj_edges[j] and i + j not in exclude_from_memo)
        print("all edges", len(all_edges))
        if drill_set is not None:
            exclude_from_memo = all_edges - drill_set
            print(len(exclude_from_memo), len(drill_set))

        num = 1 if drill_set is None else len(exclude_from_memo) // self.max_cycles_per_buffer[edge_buffer] + 1
        print(num)
        while len(exclude_from_memo) < total_cases:
            scramble, memo = self.generate_random_edge_memo(all_edges, edge_buffer, exclude_from_memo)
            if not return_list:
                print(f'Num: {num}/{max_number_of_times}')
                print(scramble, end="")

                with open(f"drill_save.json", "r+") as f:
                    drill_list_json = json.load(f)
                with open(f"drill_save.json", "w") as f:
                    drill_list_json[edge_buffer] = list(all_edges - exclude_from_memo)
                    json.dump(drill_list_json, f, indent=4)

                if input() == 'quit':
                    return
                if translate_memo:
                    print("Memo:", ', '.join(
                        list(convert_letterpairs(memo.split(), direction="loc_to_letter", piece_type="edges",
                                                 return_type='list')))
                          )
                else:
                    print(memo)

            comms = []
            for pair in memo.split():
                exclude_from_memo.add(pair)
                a, b = pair[:2], pair[2:]
                comm = MAX_COMMS[edge_buffer][a][b]
                comms.append(comm)
                if not return_list:
                    print(comm)

            scrams[num] = [scramble, memo, comms]

            num += 1

            if not return_list:
                if input() == 'quit':
                    return
        print("Finished")
        with open(f"drill_save.json", "r+") as f:
            drill_list_json = json.load(f)
        with open(f"drill_save.json", "w") as f:
            drill_list_json[edge_buffer] = []
            json.dump(drill_list_json, f, indent=4)
        return scrams

    def drill_corner_buffer(self, corner_buffer: str, exclude_from_memo: set = None, return_list=False,
                            translate_memo=False):

        # todo add edge flips hahaha
        scrams = {}
        total_cases = self.total_cases_per_buffer[corner_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[corner_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        corners = self.cube_memo.remove_irrelevant_corner_buffers(self.cube_memo.adj_corners.copy(), corner_buffer)
        all_corners = set(i + j for i, j in itertools.permutations(corners, 2) if
                          i != self.cube_memo.adj_corners[j][0] and i != self.cube_memo.adj_corners[j][1]
                          and i + j not in exclude_from_memo)

        num = 1
        while len(exclude_from_memo) < total_cases:

            scramble, memo = self.generate_random_corner_memo(all_corners, corner_buffer, exclude_from_memo)

            if translate_memo:
                print("Memo:", ', '.join(
                    list(convert_letterpairs(memo.split(), direction="loc_to_letter", piece_type="edges",
                                             return_type='list')))
                      )
                # this is the proper way to do this
                # memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

            if not return_list:
                print(f'Num: {num}/{max_number_of_times}')
                print("Scramble:", scramble, end="")
                input()
                print("Memo:", ', '.join(
                    list(convert_letterpairs(memo.split(), direction="loc_to_letter", piece_type="corners"))))

            comms = []
            for pair, pair_letters in zip(memo.split(),
                                          list(convert_letterpairs(memo.split(), direction="loc_to_letter",
                                                                   piece_type="corners", return_type='list'))):
                exclude_from_memo.add(pair)
                a, b = pair[:3], pair[3:]
                comm = MAX_COMMS[corner_buffer][a][b]
                comms.append(comm)
                if not return_list:
                    print(f"{pair_letters}:", comm)

            scrams[num] = [scramble, memo, comms]

            num += 1

            if not return_list:
                input()
        print("Finished")
        return scrams

    # memo
    def generate_random_edge_memo(self, edges, edge_buffer=None, exclude_from_memo=None, translate_memo=False):
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = self.cube_memo.default_edge_buffer if edge_buffer is None else edge_buffer
        memo = []

        edges = edges - exclude_from_memo
        for pair in edges:
            edge, edge2 = pair[:len(pair) // 2], pair[len(pair) // 2:]

            if edge == self.cube_memo.adj_edges[edge2]:
                continue
            if set(memo).intersection({edge, edge2, self.cube_memo.adj_edges[edge], self.cube_memo.adj_edges[edge2]}):
                continue

            memo.extend([edge, edge2])

        if len(memo) % 2 == 1:
            memo.pop()

        # get scramble
        scramble = self.cube_memo.scramble_edges_from_memo(memo, str(edge_buffer))

        if translate_memo:
            memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

        return scramble, self.cube_memo.format_edge_memo(memo)

    def generate_random_corner_memo(self, corners, corner_buffer=None, exclude_from_memo: set = None,
                                    translate_memo=False):

        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = self.cube_memo.default_edge_buffer if corner_buffer is None else corner_buffer
        memo = []
        memo_set = set()
        corners = corners - exclude_from_memo
        for pair in corners:
            corner, corner2 = pair[:len(pair) // 2], pair[len(pair) // 2:]

            corner_adj1, corner_adj2 = self.cube_memo.adj_corners[corner]
            corner2_adj1, corner2_adj2 = self.cube_memo.adj_corners[corner2]
            if memo_set.intersection(
                    {corner, corner_adj1, corner_adj2, corner2, corner2_adj1, corner2_adj2}):
                continue

            memo.extend([corner, corner2])

            memo_set |= {corner, corner2}

            if len(memo) == (2 * self.max_cycles_per_buffer[corner_buffer]):
                break

        if len(memo) % 2 == 1:
            memo.pop()

        scramble = self.cube_memo.scramble_edges_from_memo(memo, str(edge_buffer))

        if translate_memo:
            memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

        return scramble, self.cube_memo.format_edge_memo(memo)

    # memo
    def drill_edge_sticker(self, sticker_to_drill, single_cycle=True, return_list=False, cycles_to_exclude: set = None,
                           invert=False, algs: set = None, no_repeat=True):
        from solution import Solution
        """This is a brute force gen and check method to generate scrambles with a certain set of letter pairs"""
        # todo support starting from any buffer
        # support default certain alternate pseudo edge swaps depending on last corner target
        scrambles = []
        all_edges = self.cube_memo.default_edges.copy()
        buffer = self.cube_memo.default_edge_buffer
        buffer_adj = self.cube_memo.adj_edges[buffer]
        all_edges.remove(buffer)
        all_edges.remove(buffer_adj)

        adj = self.cube_memo.adj_edges[sticker_to_drill]
        all_edges.remove(sticker_to_drill)
        all_edges.remove(adj)
        if algs is not None:
            algs_to_drill = algs
        elif not invert:
            algs_to_drill = {sticker_to_drill + i for i in all_edges}
        else:
            algs_to_drill = {i + sticker_to_drill for i in all_edges}
        # todo optionally inject list of algs to drill
        # algs_to_drill = {'DBDR'}

        print("algs to drill", algs_to_drill)
        number = 0
        max_wait_time = 20
        if cycles_to_exclude is not None:
            algs_to_drill = algs_to_drill.difference(cycles_to_exclude)

        if single_cycle:
            frequency = 1
        else:
            frequency = int(input("Enter freq (recommended less than 3): "))
        # I don't recommend going above 2 else it will take forever
        start = time.time()
        while len(algs_to_drill) >= frequency:
            # scramble = get_scrambles.gen_premove(20, 25)
            scramble = get_scrambles.gen_premove(10, 15)
            cube = Memo(scramble, can_parity_swap=True, ls=self.cube_memo.ls)
            edge_memo = cube.format_edge_memo(cube.memo_edges()).split(' ')
            no_cycle_break_edge_memo = set()
            last_added_pair = ''
            edge_buffers = cube.edge_memo_buffers
            for pair in edge_memo:
                pair_len_half = len(pair) // 2
                a = pair[:pair_len_half]
                b = pair[pair_len_half:]

                if a in edge_buffers or b in edge_buffers:
                    break
                last_added_pair = pair
                no_cycle_break_edge_memo.add(pair)
            end = time.time()
            if (end - start) > max_wait_time and frequency:
                print(f"dropping the frequency from {frequency} to {frequency - 1}")
                frequency -= 1
                start = time.time()
            # avoid missing a cycle due to breaking into a flipped edge
            if last_added_pair in algs_to_drill and (len(cube.flipped_edges) // 2) % 2 == 1:
                continue

            algs_in_scramble = algs_to_drill.intersection(no_cycle_break_edge_memo)
            if len(algs_in_scramble) >= frequency:
                if not return_list:
                    number += 1
                    print(number, len(algs_to_drill), "Scramble:", scramble)
                    # todo make it so if you're no_repeat then allow to repeat the letter pairs
                    response = input('Enter "r" to repeat letter pairs: ')
                    if response == 'm':
                        Solution(scramble).display()
                        scrambles.append(scramble)
                        response = input('Enter "r" to repeat letter pair(s): ')

                    if response != 'r' and no_repeat:
                        algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                    print()
                    start = time.time()
                else:
                    algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                scrambles.append(scramble)
        if algs_to_drill:
            print(algs_to_drill)
        if return_list:
            return scrambles

    # memo
    def reduce_scramble(self, scramble=None, disp_time_taken=False):
        if scramble is None:
            scramble = " ".join(self.scramble)
        cube = Cube(scramble)
        if disp_time_taken:
            print("--------______---------")
            print('Now reducing scramble')
        start = time.time()

        reduced_scramble = self.cube_memo.get_solution(max_depth=min(len(scramble.split()), 20))

        end = time.time()
        if disp_time_taken:
            print(f'Time: {end - start:.3f}')
            print("--------______---------")
            print('Done')

        # print(len(scramble.split()), len(reduced_scramble.split()))
        return cube.invert_solution(reduced_scramble)

    def remove_piece(self, target_list, piece, ltr_scheme):
        piece_adj1, piece_adj2 = self.adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    # memo
    def generate_random_pair(self, target_list, ltr_scheme):
        first = random.choice(target_list)
        self.remove_piece(target_list, first, ltr_scheme)
        second = random.choice(target_list)
        return first + second

    def get_all_buffer_targets(self, buffer, piece_type='is this really needed idk'):
        if piece_type == 'corners':
            corner_buffer = buffer
            corners = self.cube_memo.remove_irrelevant_corner_buffers(self.cube_memo.adj_corners.copy(), corner_buffer)
            all_corners = set(i + j for i, j in itertools.permutations(corners, 2) if
                              i != self.cube_memo.adj_corners[j][0] and i != self.cube_memo.adj_corners[j][1])
            return all_corners
        elif piece_type == 'edges':
            edge_buffer = buffer
            edges = self.cube_memo.remove_irrelevant_edge_buffers(self.cube_memo.adj_edges, edge_buffer)

            all_edges = set(i + j for i, j in itertools.permutations(edges, 2) if
                            i != self.cube_memo.adj_edges[j])
            return all_edges
        else:
            raise Exception('put "corners" or "edges" in params pls')

    def drill_ltct(self, algs=""):
        # we are now going to pretent that we know what we are dioing
        algs_done = set()
        while True:
            while True:
                # get parity scramble
                scramble = get_scrambles.get_scramble(requires_parity=True)
                self.cube_memo = Memo(scramble)
                twisted_corners = self.cube_memo.twisted_corners
                twisted_corner_count = self.cube_memo.twisted_corners_count
                corner_memo = self.cube_memo.memo_corners()
                # check last parity target
                if twisted_corner_count == 1 and 'U' in corner_memo.pop() and 'U' in next(
                        iter(twisted_corners.values())):
                    break
            print(scramble, end="")
            while (alg := input().lower()) == "" and len(alg) != 2:
                continue
            algs_done.add(alg.strip())
            print(len(algs_done))


if __name__ == "__main__":
    # todo add translate UR to B and B to UR function
    drill = Drill()
    print(convert_letterpairs(drill.get_all_buffer_targets("UFL", 'corners'), 'loc_to_letters', 'corners'))
    # drill.drill_edge_sticker(sticker_to_drill="FD", single_cycle=True, return_list=False,
    #                          cycles_to_exclude=
    #                          {'FDRB', 'FDDB', 'FDDL', 'FDFR', 'FDLF', 'FDBR', 'FDBL', 'FDBU', 'FDRU', 'FDLU', 'FDUL',
    #                           'FDLD', 'FDUR', 'FDBD', 'FDUB', 'FDFL', 'FDLB', 'FDRD', 'FDRF'}
    #                          )

    # memo = drill.generate_random_edge_memo("UF", translate_memo=True)

    # print(memo)
    # drill.drill_edge_buffer("UB", exclude_from_memo=set(), return_list=False)
    # drill.drill_edge_sticker("DB", invert=True)  # todo rename invert
    # algs = {'BDLF', 'RBUL', 'RDRF', 'BULF', 'BDFD', 'FLFR', 'BRLF', 'DLRF', 'UBBL', 'RULD',
    #         'BUUR', 'RFUL', 'FLLD', 'URRF', 'LDLB', 'UBFD', 'RUDL', 'RFBL', 'LDBU', 'ULFL',
    #         }
    algs = convert_letterpairs(
        [
            "LG", "BP", "AI", "SO", "HG", "GL", "ZX", "XV", "NX", "VW", "OG", "XS", "CB",
            "SR", "GW", "IZ", "PS", "DB", "NJ", "CZ", "FW", "GT", "OJ"
        ],
        direction="letter_to_loc", piece_type="edges"
    )
    # "OJ",
    print(algs)
    print(len(algs))
    # buffer = "UFR"
    # result = ''
    # print(result)
    # drill.drill_corner_buffer('UBL')
    drill.drill_edge_buffer("DL", translate_memo=True)
    # drill.drill_edge_sticker("DB", algs=algs, single_cycle=False)

    # # max_num = drill.max_cycles_per_buffer
    # # print(max_num)

    a = {'UR': 'RU', 'UL': 'LU', 'LU': 'UL', 'LF': 'FL', 'LD': 'DL', 'LB': 'BL', 'FR': 'RF', 'FD': 'DF', 'FL': 'LF',
         'RU': 'UR', 'RB': 'BR', 'RD': 'DR', 'RF': 'FR', 'BL': 'LB', 'BD': 'DB', 'BR': 'RB', 'DF': 'FD', 'DR': 'RD',
         'DB': 'BD', 'DL': 'LD'}

    # print(len(list(permutations(a, 2))))
    # print(permutations(a, 2))
    # UB 2:08:00.00
    # UB   53:00.00
    # UL 1:40.59.77

# UL: ON GH OJ OR JN NO XI HJ IT HI WV LJ IH HS TV PR

# NL ?
# TV last U last move R U R U' R' U' R' U' R U
# RP L u L' OR U'
# FW l u' L
# VT no AUF
# NF u' R' U' R
# SO r' might be better than MUD
# RJ U' L' U L'
# CV R2 U'
# GN U' F R'
# CS l' M' RH
# VW R2 U'
# PH u'
# LJ U' L
# JL U' R'
# JH u R2'
# IF M' U2
# LH U' LH regrip
# TI F' R
# FT U'
# IS U2
# SI U2
# TH U
# XV S L2' S' L2
# TP U'


"ON",
"GH",
"OJ",
"OR",
"JN",
"NO",
"XI",
"HJ",
"IT",
"HI",
"WV",
"LJ",
"IH",
"HS",
"TV",
"PR ",
"NL",
"TV",
"RP",
"FW",
"VT",
"NF",
"SO",
"RJ",
"CV",
"GN",
"CS",
"VW",
"PH",
"LJ",
"JL",
"JH",
"IF",
"LH",
"TI",
"FT",
"IS",
"SI",
"TH",
"XV",
"TP",

# UBL
"""
DK, LH, EZ, TC, DC, FW, VE, HL, CH, SE, EG, ZE, WP, EP, PS, SC
GO D2'
U2 R2' U' R2 D R2' U R2 U' R2' D' R2 U': U2 U' D
ZL D2'
LT KS D2'
GV U
OG D' U'
GH D' R' D' R D R' U R D' R' U' D R D:   D' R' UBR AS
PH PEACH D R' U R D2' R' U' R D2 D'
PC D R D' L2' D R' D' L2
HG <RUL> or <RUD> ??
PW D
VG U
ZG D'
PE U' FK
GP U
GS D2'
SD D'
LZ: D' R2 U'
WE U'D'
"""
#
# from itertools import permutations
#
# a = permutations(['C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'O', 'P', 'S', 'T', 'V', 'W', 'Z'], r=2)
# a = list(a)
# print(a)
# print(len(a))
# b = [i + j for i, j in a]
# print(set(b))

# DL
# NR R' E' R E R S' R' S
# RN S' R S R' E' R' E R  you can also do it with wide Rs
