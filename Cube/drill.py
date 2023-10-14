import itertools
import json
import random
import time

import kociemba

import get_scrambles
from Cube import Cube
from Cube.letterscheme import LetterScheme, convert_letterpairs
from Cube.letterscheme import letter_scheme
from Cube.memo import Memo
from comms import COMMS


class Drill:

    def __init__(self, memo: Memo = None, buffer_order=None):
        if memo is not None:
            self.cube_memo: Memo = memo
        else:
            self.cube_memo: Memo = Memo(buffer_order=buffer_order)

        self.max_cycles_per_buffer = {buffer: (8 - i) // 2 for i, buffer in
                                      enumerate(self.cube_memo.corner_buffer_order, 1)}
        self.max_cycles_per_buffer |= {buffer: (12 - i) // 2 for i, buffer in
                                       enumerate(self.cube_memo.edge_buffer_order, 1)}

        self.total_cases_per_edge_buffer = [i * (i - 2) for i in range(22, 2, -2)]
        self.total_cases_per_corner_buffer = [i * (i - 3) for i in range(21, 3, -3)]
        self.total_cases_per_buffer = {
            buffer: num for buffer, num in
            zip(self.cube_memo.edge_buffer_order + self.cube_memo.corner_buffer_order,
                self.total_cases_per_edge_buffer + self.total_cases_per_corner_buffer)
        }

    # memo
    def generate_drill_list(self, ltr_scheme: LetterScheme, buffer, target):
        # pick what letter scheme to use
        # how to separate c from e
        # just doing corners first
        all_targets = ltr_scheme.get_corners()
        self.remove_piece(all_targets, buffer)

        # random_list = []
        # # generate random pair
        # for _ in range(18):
        #     target_list = all_targets[:]
        #     random_list.append(generate_random_pair(target_list, ltr_scheme))

        target_list = all_targets[:]
        # remove buffer stickers
        self.remove_piece(target_list, target)

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

        cube = Memo(scramble, ls=self.cube_memo.ls)
        corner_memo = self.cube_memo.format_corner_memo(cube.memo_corners()).split(' ')
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

    # memo
    # def drill_corner_sticker(self, sticker_to_drill):
    #     #             # todo make it so if you're no_repeat then allow to repeat the letter pairs
    #     #     return scrambles
    #     # todo fix buffer thing
    #     algs_to_drill = self.generate_drill_list(self.cube_memo.ls, self.cube_memo.default_corner_buffer,
    #                                              sticker_to_drill)
    #
    #     alg_freq_dist = {str(pair): 0 for pair in algs_to_drill}
    #     # print(type(alg_freq_dist))
    #     # print('Running...')
    #     count = 2
    #     inc_amt = 2
    #     while True:
    #         scramble, alg_to_drill = self.get_target_scramble(algs_to_drill)
    #         # check if freq is < count and if so continue
    #         if alg_freq_dist[alg_to_drill] < count:
    #             alg_freq_dist[alg_to_drill] += 1
    #         elif len(set(alg_freq_dist.values())) == 1:
    #             print("Increasing count")
    #             count += inc_amt
    #         else:
    #             continue
    #
    #         print(scramble, end="")
    #
    #         input()

    def drill_corner_sticker(self, sticker_to_drill):

        def remove_piece(target_list, piece, ltr_scheme):
            piece_adj1, piece_adj2 = Cube(ls=ltr_scheme).adj_corners[piece]
            target_list.remove(piece)
            target_list.remove(piece_adj1)
            target_list.remove(piece_adj2)
            return target_list

        def generate_drill_list(ltr_scheme: LetterScheme, buffer, target):
            all_targets = LetterScheme(use_default=False).get_corners()
            remove_piece(all_targets, buffer, ltr_scheme)

            target_list = all_targets[:]
            # remove buffer stickers
            remove_piece(target_list, target, ltr_scheme)

            # generate random pairs
            # generate specific pairs
            # generate target groups e.g. just Z or H and k
            # generate inverse target groups
            # specify buffer
            return {target + i for i in target_list}

        sticker_to_drill = sticker_to_drill

        algs_to_drill = generate_drill_list(letter_scheme, "U", sticker_to_drill)
        number = 0
        # fixme drill just one sticker with s XY -onlypairIwanttodrill
        # algs_to_drill = {"NS"}
        alg_freq_dist = {str(pair): 0 for pair in algs_to_drill}
        print(type(alg_freq_dist))
        print('Running...')
        count = 2
        inc_amt = 2

        while algs_to_drill:
            scramble = get_scrambles.get_scramble()
            cube = Memo(scramble, ls=letter_scheme)
            corner_memo = cube.format_corner_memo(cube.memo_corners()).split(' ')
            no_cycle_break_corner_memo = set()

            # if just the first target of the memo is the target eg: L then cycle break, this is bad

            corner_buffers = cube.corner_memo_buffers
            for pair in corner_memo:
                if len(pair) == 4 or len(pair) == 2:
                    pair_len_half = len(pair) // 2
                    a = pair[:pair_len_half]
                    b = pair[pair_len_half:]
                else:
                    a = pair
                    b = ''
                if a in corner_buffers or b in corner_buffers:
                    break
                no_cycle_break_corner_memo.add(pair)

            alg_to_drill = algs_to_drill.intersection(no_cycle_break_corner_memo)

            if algs_to_drill.intersection(no_cycle_break_corner_memo):
                alg_to_drill = alg_to_drill.pop()
                algs_to_drill -= algs_to_drill.intersection(no_cycle_break_corner_memo)
                # check if freq is < count and if so continue
                if alg_freq_dist[alg_to_drill] < count:
                    alg_freq_dist[alg_to_drill] += 1
                elif len(set(alg_freq_dist.values())) == 1:
                    count += inc_amt
                else:
                    continue

                print(scramble)
                input()

    def drill_edge_buffer_cycle_breaks(self, edge_buffer: str):
        edges = self.cube_memo.remove_irrelevant_edge_buffers(self.cube_memo.adj_edges, edge_buffer)
        all_edges = [i + j for i, j in itertools.permutations(edges, 2) if
                     i != self.cube_memo.adj_edges[j]]
        all_edges += all_edges
        random.shuffle(all_edges)

        rand_edges = random.choices(all_edges, k=len(all_edges) // 2)
        cube = Cube()
        for pair in rand_edges:
            a, b = pair[:len(pair) // 2], pair[len(pair) // 2:]
            buffer = COMMS[str(edge_buffer)]
            comm = buffer[a][b]
            cube.scramble_cube(comm)

        scram = kociemba.solve(cube.get_faces_colors(), max_depth=19)

        return scram

    def drill_corner_buffer_cycle_breaks(self, corner_buffer: str):
        corners = self.cube_memo.remove_irrelevant_corner_buffers(self.cube_memo.adj_corners.copy(), corner_buffer)
        all_corners = [i + j for i, j in itertools.permutations(corners, 2) if
                       i != self.cube_memo.adj_corners[j]]
        all_corners += all_corners
        random.shuffle(all_corners)

        rand_corners = random.choices(all_corners, k=len(all_corners) // 2)
        cube = Cube()
        for pair in rand_corners:
            a, b = pair[:len(pair) // 2], pair[len(pair) // 2:]
            buffer = COMMS[str(corner_buffer)]
            comm = buffer[a][b]
            cube.scramble_cube(comm)

        scram = kociemba.solve(cube.get_faces_colors(), max_depth=20)

        return scram

    # memo
    def drill_edge_buffer(self, edge_buffer: str, exclude_from_memo=None, return_list=False, translate_memo=False,
                          drill_set: set | None = None, random_pairs=False, file_comms=None):
        # todo add edge flips hahaha
        scrams = {}
        total_cases = self.total_cases_per_buffer[edge_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[edge_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        edges = self.cube_memo.remove_irrelevant_edge_buffers(self.cube_memo.adj_edges, edge_buffer)

        all_edges = set(i + j for i, j in itertools.permutations(edges, 2) if
                        i != self.cube_memo.adj_edges[j] and i + j not in exclude_from_memo)
        # all_edges = list(all_edges)
        # random.shuffle(all_edges)
        # all_edges = set(all_edges)
        if drill_set is not None:
            exclude_from_memo = all_edges - drill_set

        num = 1 if drill_set is None else len(exclude_from_memo) // self.max_cycles_per_buffer[edge_buffer] + 1

        while len(exclude_from_memo) < total_cases or random_pairs:
            scramble, memo = self.generate_random_edge_memo(all_edges, edge_buffer, exclude_from_memo,
                                                            random_pairs=random_pairs)

            if not return_list:
                if random_pairs:
                    print(f'Scramble: "{scramble}"')
                else:
                    print(f'Scramble {num}/{max_number_of_times}: "{scramble}"')

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

            print()
            comms = []
            for pair, pair_letters in zip(memo.split(),
                                          list(convert_letterpairs(memo.split(), direction="loc_to_letter",
                                                                   piece_type="edges", return_type='list'))):
                exclude_from_memo.add(pair)
                a, b = pair[:2], pair[2:]
                comm = file_comms[edge_buffer][a][b]
                comms.append(comm)
                if not return_list:
                    print(f"{pair_letters}:", comm)

            scrams[num] = [scramble, memo, comms]

            num += 1
            print("-" * 25)

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

    def drill_corner_buffer(self, corner_buffer: str, exclude_from_memo: set = None, return_list: bool = False,
                            drill_set: set = None, random_pairs=False, file_comms=None):

        # todo add edge flips hahaha
        scrams = {}
        total_cases = self.total_cases_per_buffer[corner_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[corner_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        corners = self.cube_memo.remove_irrelevant_corner_buffers(self.cube_memo.adj_corners.copy(), corner_buffer)
        all_corners = set(i + j for i, j in itertools.permutations(corners, 2) if
                          i != self.cube_memo.adj_corners[j][0] and i != self.cube_memo.adj_corners[j][1]
                          and i + j not in exclude_from_memo)

        if drill_set is not None:
            exclude_from_memo = all_corners - drill_set

        num = 1 if drill_set is None else len(exclude_from_memo) // self.max_cycles_per_buffer[corner_buffer] + 1
        while len(exclude_from_memo) < total_cases or random_pairs:

            scramble, memo = self.generate_random_corner_memo(all_corners, corner_buffer, exclude_from_memo,
                                                              random_pairs=random_pairs)

            # this is the proper way to do this
            # memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

            if not return_list:
                if random_pairs:
                    print(f'Scramble: "{scramble}"')
                else:
                    print(f'Scramble {num}/{max_number_of_times}: "{scramble}"')

                with open(f"drill_save.json", "r+") as f:
                    drill_list_json = json.load(f)
                with open(f"drill_save.json", "w") as f:
                    drill_list_json[corner_buffer] = list(all_corners - exclude_from_memo)
                    json.dump(drill_list_json, f, indent=4)

                if input() == 'quit':
                    return

                print("Memo:", ', '.join(
                    list(convert_letterpairs(memo.split(), direction="loc_to_letter", piece_type="corners"))))
                print()
            comms = []
            for pair, pair_letters in zip(memo.split(),
                                          list(convert_letterpairs(memo.split(), direction="loc_to_letter",
                                                                   piece_type="corners", return_type='list'))):
                exclude_from_memo.add(pair)
                a, b = pair[:3], pair[3:]
                comm = file_comms[corner_buffer][a][b]
                if not comm:
                    comm = COMMS[corner_buffer][a][b]
                comms.append(comm)
                if not return_list:
                    print(f"{pair_letters}:", comm)

            scrams[num] = [scramble, memo, comms]

            num += 1

            print("-" * 25)

            if not return_list:
                if input() == 'quit':
                    return

        print("Finished")
        with open(f"drill_save.json", "r+") as f:
            drill_list_json = json.load(f)
        with open(f"drill_save.json", "w") as f:
            drill_list_json[corner_buffer] = []
            json.dump(drill_list_json, f, indent=4)
        return scrams

    # memo
    def generate_random_edge_memo(self, edges, edge_buffer=None, exclude_from_memo=None, translate_memo=False,
                                  random_pairs=False):
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = self.cube_memo.default_edge_buffer if edge_buffer is None else edge_buffer
        memo = []

        if random_pairs:
            edges = list(edges)
            random.shuffle(edges)
        else:
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

    def generate_random_corner_memo(self, corners: set, corner_buffer=None, exclude_from_memo: set = None,
                                    translate_memo=False, random_pairs=False):

        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        corner_buffer = self.cube_memo.default_corner_buffer if corner_buffer is None else corner_buffer
        memo = []
        memo_set = set()
        if random_pairs:
            corners = list(corners)
            random.shuffle(corners)
        else:
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

        scramble = self.cube_memo.scramble_corners_from_memo(memo, str(corner_buffer))

        if translate_memo:
            memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

        return scramble, self.cube_memo.format_corner_memo(memo)

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
        len_algs_to_drill = len(algs_to_drill)
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
                    print(f"Scramble {number}/{len_algs_to_drill}:", scramble)
                    # todo make it so if you're no_repeat then allow to repeat the letter pairs
                    response = input('Enter "r" to repeat letter pairs: ')
                    if response == 'm':
                        Solution(scramble, buffer_order=self.cube_memo.buffer_order).display()
                        scrambles.append(scramble)
                        response = input('Enter "r" to repeat letter pair(s): ')

                    if response != 'r' and no_repeat:
                        algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                    print()
                    start = time.time()
                    if response == 'q' or response == 'quit':
                        return
                else:
                    algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                scrambles.append(scramble)
        if algs_to_drill:
            print(algs_to_drill)
        if return_list:
            return scrambles

    # memo
    def reduce_scramble(self, scramble, disp_time_taken=False):
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
        return self.cube_memo.invert_solution(reduced_scramble)

    def remove_piece(self, target_list, piece):
        piece_adj1, piece_adj2 = self.cube_memo.adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    # memo
    def generate_random_pair(self, target_list, ltr_scheme):
        first = random.choice(target_list)
        self.remove_piece(target_list, first)
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

    def drill_ltct(self):
        # we are now going to pretent that we know what we are dioing
        # todo this is where drill ltct goes
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
    a = drill.total_cases_per_corner_buffer
    b = drill.total_cases_per_edge_buffer
    print(a, b)
    s = drill.drill_edge_buffer_cycle_breaks("UB")
    print(s)

    quit()
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

    algs = {'UR': 'RU', 'UL': 'LU', 'LU': 'UL', 'LF': 'FL', 'LD': 'DL', 'LB': 'BL', 'FR': 'RF', 'FD': 'DF', 'FL': 'LF',
            'RU': 'UR', 'RB': 'BR', 'RD': 'DR', 'RF': 'FR', 'BL': 'LB', 'BD': 'DB', 'BR': 'RB', 'DF': 'FD', 'DR': 'RD',
            'DB': 'BD', 'DL': 'LD'}

    # print(len(list(permutations(algs, 2))))
    # print(permutations(algs, 2))
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
# TP U' R'
DL_comms = [
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
]
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
# algs = permutations(['C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'O', 'P', 'S', 'T', 'V', 'W', 'Z'], r=2)
# algs = list(algs)
# print(algs)
# print(len(algs))
# b = [i + j for i, j in algs]
# print(set(b))

# DL
# NR R' E' R E R S' R' S
# RN S' R S R' E' R' E R  you can also do it with wide Rs


# DL 1:42.84
# DL 1:00.83
# DL 1:05.94
# DL   59.09
# DL   51.51 did i actually do all the cases tho
# DL   51.79
# DL   50.30
# DL   47.76
# DL   47.82
# DL   43.70 (5.46 per case)


# DR 7:36
# DR 6:54.06
# DR 5:08.67
# DR 3:37.48
# DR 4:08.39
# DR 3:07.88
# DR 3:45.56
# DR 2:44.34
# DR 3:04.97
# DR 2:43.51
# DR 2:43.14
# DR 2:23.99 5.999583333333333
# DR 2:24.63

# DB 35:46.151

# 2 flips 1824.52 33:24.52

# FR 6:41.75
