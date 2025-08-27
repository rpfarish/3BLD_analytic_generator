import itertools
import json
import random
import time

import dlin
from comms.comms import COMMS
from Cube import Cube
from Cube.letterscheme import LetterScheme, convert_letterpairs
from Cube.memo import Memo
from Scramble import get_scramble

DEBUG = 0


class Drill:

    def __init__(self, memo: Memo = None, buffer_order=None, letter_scheme=None):
        if memo is not None:
            self.cube_memo: Memo = memo
        else:
            self.cube_memo: Memo = Memo(buffer_order=buffer_order)

        if letter_scheme is None:
            self.letter_scheme = LetterScheme()
            # raise Exception("Panic there is no letterscheme set in drill")
        else:
            self.letter_scheme = letter_scheme

        self.max_cycles_per_buffer = {
            buffer: (8 - i) // 2
            for i, buffer in enumerate(self.cube_memo.corner_buffer_order, 1)
        }
        self.max_cycles_per_buffer |= {
            buffer: (12 - i) // 2
            for i, buffer in enumerate(self.cube_memo.edge_buffer_order, 1)
        }

        self.total_cases_per_edge_buffer = [i * (i - 2) for i in range(22, 2, -2)]
        self.total_cases_per_corner_buffer = [i * (i - 3) for i in range(21, 3, -3)]
        self.total_cases_per_buffer = {
            buffer: num
            for buffer, num in zip(
                self.cube_memo.edge_buffer_order + self.cube_memo.corner_buffer_order,
                self.total_cases_per_edge_buffer + self.total_cases_per_corner_buffer,
            )
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
        scramble = get_scramble.get_scramble()

        cube = Memo(scramble, ls=self.cube_memo.ls)
        corner_memo = self.cube_memo.format_corner_memo(cube.memo_corners()).split(" ")
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
                b = ""
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

    def get_no_cycle_break_memo_corners(
        self, scramble, letter_scheme, buffer, format=True
    ) -> list[str]:

        if (len(scramble.split()) - scramble.count("2")) % 2 == 1:
            swap = ("UF", "UR")
        else:
            swap = None

        trace = dlin.trace(scramble, swap=swap)

        corner_cycles = trace["corner"]
        corner_targets = None
        for cycle in corner_cycles:
            # TODO: add buffer from settings and load buffer order from settings
            if cycle["buffer"] == buffer and cycle["targets"]:
                corner_targets = cycle["targets"]
                break

        # print("corner targets", corner_targets)
        if not corner_targets:
            return []

        if len(corner_targets) % 2 != 0:
            corner_targets.pop()

        if not corner_targets:
            return []

        if not format:
            return corner_targets

        return " ".join(
            f"{corner_targets[i]}{corner_targets[i + 1]}"
            for i in range(0, len(corner_targets) - 1, 2)
        ).split(" ")

    def drill_corner_sticker(
        self,
        algs_to_drill: set,
        letter_scheme=None,
        buffer=None,
        random_pairs: bool = False,
        freq: int = -1,
    ):

        # if algs is not None:
        #     algs_to_drill = algs
        # else:
        #     algs_to_drill = self.generate_drill_list(
        #         letter_scheme, buffer, sticker_to_drill
        #     )
        #
        # if cycles_to_exclude is not None:
        #     algs_to_drill -= cycles_to_exclude

        print("Running...")
        number = 0

        tries = 0
        max_tries = 3000

        all_algs_to_drill = algs_to_drill.copy()
        remaining_algs = algs_to_drill.copy()
        len_remaining_algs = len(algs_to_drill)

        cycle_count = 3 if len(remaining_algs) > 60 else 2
        cycle_count = 1 if len(remaining_algs) < 20 else cycle_count

        # Initialize timing lists before the while loop
        memo_times = []

        start = time.perf_counter()
        while remaining_algs:

            # todo maybe increase scramble length to 26?
            scramble = get_scramble.get_scramble_bld()

            memo = self.get_no_cycle_break_memo_corners(scramble, letter_scheme, buffer)

            # Time intersection
            cycles_to_drill = remaining_algs.intersection(set(memo))

            if tries == max_tries or (
                (time.perf_counter() - start) > 2 and cycle_count > 2
            ):
                cycle_count -= 1
                tries = 0

            if len(cycles_to_drill) < cycle_count and tries < max_tries:
                tries += 1
                continue

            if cycles_to_drill:
                memo_times.append(time.perf_counter() - start)

                print(memo_times[-1])
                # TODO: make heuristic better
                cycle_count = 3 if len(remaining_algs) > 60 else 2
                cycle_count = 1 if len(remaining_algs) < 20 else cycle_count

                number += 1
                tries = 0
                print(f"Scramble {number}/{len_remaining_algs}: {scramble}")

                algs_used_ls = convert_letterpairs(
                    [comm for comm in memo if comm in all_algs_to_drill],
                    "loc_to_letter",
                    letter_scheme,
                    return_type="list",
                )

                remaining_algs_ls = convert_letterpairs(
                    remaining_algs,
                    "loc_to_letter",
                    letter_scheme,
                    return_type="list",
                )

                response = input()

                if response == "q" or response == "quit":
                    return

                print(
                    "Algs used:",
                    ", ".join(
                        [
                            (f"'{i}'" if i not in remaining_algs_ls else i)
                            for i in algs_used_ls
                        ]
                    ),
                )

                response = input('Enter "r" to repeat letter pairs: ')

                if response == "q" or response == "quit":
                    return

                if response == "r":
                    len_remaining_algs += len(cycles_to_drill)
                    print()
                    continue

                remaining_algs = remaining_algs.difference(cycles_to_drill)
                if len(cycles_to_drill) > 1:
                    len_remaining_algs -= len(cycles_to_drill) - 1

                remaining_algs -= remaining_algs.intersection(set(memo))
                print()
                start = time.perf_counter()

        print(
            f"Memo - Avg: {sum(memo_times)/len(memo_times):.3f}s, Min: {min(memo_times):.3f}s, Max: {max(memo_times):.3f}s"
        )

    def drill_two_color_memo(
        self,
        letter_scheme=None,
        buffer=None,
    ):

        print("Running...")
        while True:
            scramble = get_scramble.get_scramble()

            no_cycle_break_corner_memo = self.get_no_cycle_break_memo_corners(
                scramble, letter_scheme, format=False
            )
            DBR = "DBR", "BDR", "RDB"
            DFL = "DFL", "FDL", "LDF"
            DBL = "DBL", "BDL", "LDB"
            DFR = "DFR", "FDR", "RDF"

            for i in range(0, len(no_cycle_break_corner_memo) - 1, 2):
                DBR_to_DFL = (
                    no_cycle_break_corner_memo[i] in DBR
                    and no_cycle_break_corner_memo[i + 1] in DFL
                )
                DBL_to_DFR = (
                    no_cycle_break_corner_memo[i] in DBL
                    and no_cycle_break_corner_memo[i + 1] in DFR
                )
                if DBR_to_DFL or DBL_to_DFR:
                    print(scramble)
                    input()
                    break

    def drill_edge_buffer_cycle_breaks(self, edge_buffer: str):
        edges = self.cube_memo.remove_irrelevant_edge_buffers(
            self.cube_memo.adj_edges, edge_buffer
        )

        all_edges = [
            i + j
            for i, j in itertools.permutations(edges, 2)
            if i != self.cube_memo.adj_edges[j]
        ]
        all_edges += all_edges
        random.shuffle(all_edges)

        rand_edges = random.choices(all_edges, k=len(all_edges) // 2)
        cube = Cube()
        for pair in rand_edges:
            a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
            buffer = COMMS[str(edge_buffer)]
            comm = buffer[a][b]
            cube.scramble_cube(comm)

        scram = cube.solve(max_depth=19)

        return scram

    def drill_corner_buffer_cycle_breaks(self, corner_buffer: str):
        corners = self.cube_memo.remove_irrelevant_corner_buffers(
            self.cube_memo.adj_corners.copy(), corner_buffer
        )
        all_corners = [
            i + j
            for i, j in itertools.permutations(corners, 2)
            if i != self.cube_memo.adj_corners[j]
        ]
        all_corners += all_corners
        random.shuffle(all_corners)

        rand_corners = random.choices(all_corners, k=len(all_corners) // 2)
        cube = Cube()
        for pair in rand_corners:
            a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
            buffer = COMMS[str(corner_buffer)]
            comm = buffer[a][b]
            cube.scramble_cube(comm)

        scram = cube.solve(max_depth=19)

        return scram

    # memo
    def drill_edge_buffer(
        self,
        edge_buffer: str,
        exclude_from_memo=None,
        return_list=False,
        translate_memo=False,
        drill_set: set | None = None,
        random_pairs=False,
        file_comms=None,
    ):
        # todo add edge flips hahaha
        scrams = {}
        total_cases = self.total_cases_per_buffer[edge_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[edge_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        edges = self.cube_memo.remove_irrelevant_edge_buffers(
            self.cube_memo.adj_edges, edge_buffer
        )

        all_edges = set(
            i + j
            for i, j in itertools.permutations(edges, 2)
            if i != self.cube_memo.adj_edges[j] and i + j not in exclude_from_memo
        )
        # all_edges = list(all_edges)
        # random.shuffle(all_edges)
        # all_edges = set(all_edges)
        if drill_set is not None:
            exclude_from_memo = all_edges - drill_set

        num = (
            1
            if drill_set is None
            else len(exclude_from_memo) // self.max_cycles_per_buffer[edge_buffer] + 1
        )

        while len(exclude_from_memo) < total_cases or random_pairs:
            scramble, memo = self.generate_random_edge_memo(
                all_edges, edge_buffer, exclude_from_memo, random_pairs=random_pairs
            )

            if not return_list:
                if random_pairs:
                    print(f"Scramble: {scramble}")
                else:
                    print(f'Scramble {num}/{max_number_of_times}: "{scramble}"')

                with open(f"cache/drill_save.json", "r+") as f:
                    drill_list_json = json.load(f)
                with open(f"cache/drill_save.json", "w") as f:
                    drill_list_json[edge_buffer] = list(all_edges - exclude_from_memo)
                    json.dump(drill_list_json, f, indent=4)

                response = input().lower()
                if response.startswith("q"):
                    return

                if translate_memo:
                    print(
                        "Memo:",
                        ", ".join(
                            list(
                                convert_letterpairs(
                                    memo.split(),
                                    direction="loc_to_letter",
                                    letter_scheme=self.letter_scheme,
                                    piece_type="edges",
                                    return_type="list",
                                )
                            )
                        ),
                    )
                else:
                    print(memo)

            print()
            comms = []
            for pair, pair_letters in zip(
                memo.split(),
                list(
                    convert_letterpairs(
                        memo.split(),
                        direction="loc_to_letter",
                        letter_scheme=self.letter_scheme,
                        piece_type="edges",
                        return_type="list",
                    )
                ),
            ):
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
                if input() == "quit":
                    return
        print("Finished")
        with open(f"cache/drill_save.json", "r+") as f:
            drill_list_json = json.load(f)
        with open(f"cache/drill_save.json", "w") as f:
            drill_list_json[edge_buffer] = []
            json.dump(drill_list_json, f, indent=4)
        return scrams

    def drill_corner_buffer(
        self,
        corner_buffer: str,
        exclude_from_memo: set = None,
        return_list: bool = False,
        drill_set: set = None,
        random_pairs=False,
        file_comms=None,
    ):
        # todo add edge flips hahaha
        scrams = {}
        total_cases = self.total_cases_per_buffer[corner_buffer]
        max_number_of_times = total_cases // self.max_cycles_per_buffer[corner_buffer]
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        corners = self.cube_memo.remove_irrelevant_corner_buffers(
            self.cube_memo.adj_corners.copy(), corner_buffer
        )
        all_corners = set(
            i + j
            for i, j in itertools.permutations(corners, 2)
            if i != self.cube_memo.adj_corners[j][0]
            and i != self.cube_memo.adj_corners[j][1]
            and i + j not in exclude_from_memo
        )

        if drill_set is not None:
            exclude_from_memo = all_corners - drill_set

        num = (
            1
            if drill_set is None
            else len(exclude_from_memo) // self.max_cycles_per_buffer[corner_buffer] + 1
        )

        while len(exclude_from_memo) < total_cases or random_pairs:
            scramble, memo = self.generate_random_corner_memo(
                all_corners, corner_buffer, exclude_from_memo, random_pairs=random_pairs
            )

            if not return_list:
                if random_pairs:
                    print(f"Scramble: {scramble}")
                else:
                    print(f"Scramble {num}/{max_number_of_times}: {scramble}")

                with open(f"cache/drill_save.json", "r+") as f:
                    drill_list_json = json.load(f)
                with open(f"cache/drill_save.json", "w") as f:
                    drill_list_json[corner_buffer] = list(
                        all_corners - exclude_from_memo
                    )
                    json.dump(drill_list_json, f, indent=4)

                response = input().lower()
                if response.startswith("q"):
                    return

                print(
                    "Memo:",
                    ", ".join(
                        list(
                            convert_letterpairs(
                                memo.split(),
                                direction="loc_to_letter",
                                letter_scheme=self.letter_scheme,
                                piece_type="corners",
                            )
                        )
                    ),
                )

            print()
            comms = []
            for pair, pair_letters in zip(
                memo.split(),
                list(
                    convert_letterpairs(
                        memo.split(),
                        direction="loc_to_letter",
                        letter_scheme=self.letter_scheme,
                        piece_type="corners",
                        return_type="list",
                    )
                ),
            ):
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
                if input() == "quit":
                    return

        print("Finished")
        with open(f"cache/drill_save.json", "r+") as f:
            drill_list_json = json.load(f)
        with open(f"cache/drill_save.json", "w") as f:
            drill_list_json[corner_buffer] = []
            json.dump(drill_list_json, f, indent=4)
        return scrams
        # memo

    def generate_random_edge_memo(
        self,
        edges,
        edge_buffer=None,
        exclude_from_memo=None,
        translate_memo=False,
        random_pairs=False,
    ):
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = (
            self.cube_memo.default_edge_buffer if edge_buffer is None else edge_buffer
        )
        memo = []

        if random_pairs:
            edges = list(edges)
            random.shuffle(edges)
        else:
            edges = edges - exclude_from_memo
        for pair in edges:
            edge, edge2 = pair[: len(pair) // 2], pair[len(pair) // 2 :]

            if edge == self.cube_memo.adj_edges[edge2]:
                continue
            if set(memo).intersection(
                {
                    edge,
                    edge2,
                    self.cube_memo.adj_edges[edge],
                    self.cube_memo.adj_edges[edge2],
                }
            ):
                continue

            memo.extend([edge, edge2])

        if len(memo) % 2 == 1:
            memo.pop()

        # get scramble
        scramble = self.cube_memo.scramble_edges_from_memo(memo, str(edge_buffer))

        if translate_memo:
            memo = self.cube_memo.translate_letter_scheme(memo, translate_type="name")

        return scramble, self.cube_memo.format_edge_memo(memo)

    def generate_random_corner_memo(
        self,
        corners: set,
        corner_buffer=None,
        exclude_from_memo: set = None,
        translate_memo=False,
        random_pairs=False,
    ):
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        corner_buffer = (
            self.cube_memo.default_corner_buffer
            if corner_buffer is None
            else corner_buffer
        )
        memo = []
        memo_set = set()
        if random_pairs:
            corners = list(corners)
            random.shuffle(corners)
        else:
            corners = corners - exclude_from_memo
        for pair in corners:
            corner, corner2 = pair[: len(pair) // 2], pair[len(pair) // 2 :]

            corner_adj1, corner_adj2 = self.cube_memo.adj_corners[corner]
            corner2_adj1, corner2_adj2 = self.cube_memo.adj_corners[corner2]
            if memo_set.intersection(
                {corner, corner_adj1, corner_adj2, corner2, corner2_adj1, corner2_adj2}
            ):
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
    def drill_edge_sticker(
        self,
        sticker_to_drill,
        letter_scheme,
        single_cycle=True,
        return_list=False,
        cycles_to_exclude: set = None,
        invert=False,
        algs: set = None,
        no_repeat=True,
        buffer=None,
    ):
        from Cube.solution import Solution

        """This is a brute force gen and check method to generate scrambles with a certain set of letter pairs"""

        def remove_piece(target_list, piece, ltr_scheme):
            piece_adj1 = Cube(ls=ltr_scheme).adj_edges[piece]
            target_list.remove(piece)
            target_list.remove(piece_adj1)
            return target_list

        def generate_drill_list(ltr_scheme: LetterScheme, buffer, target, invert):
            all_targets = ltr_scheme.get_edges()
            remove_piece(all_targets, buffer, ltr_scheme)

            target_list = all_targets[:]
            # remove buffer stickers
            remove_piece(target_list, target, ltr_scheme)

            # generate random pairs
            # generate specific pairs
            # generate target groups e.g. just Z or H and k
            # generate inverse target groups
            # specify buffer
            if not invert:
                return {target + i for i in target_list}
            else:
                return {i + target for i in target_list}

        # todo support starting from any buffer
        # support default certain alternate pseudo edge swaps depending on last corner target
        scrambles = []

        if algs is not None:
            algs_to_drill = algs
        else:
            algs_to_drill = generate_drill_list(
                letter_scheme, buffer, sticker_to_drill, invert
            )
        # todo optionally inject list of algs to drill
        # algs_to_drill = {'DBDR'}

        number = 0
        max_wait_time = 20
        if cycles_to_exclude is not None:
            algs_to_drill = algs_to_drill.difference(cycles_to_exclude)
        len_algs_to_drill = len(algs_to_drill)

        if single_cycle:
            frequency = 1
        else:
            frequency = int(input("Enter freq (recommended less than 3): "))
        # I don't recommend going above 2 else it will take forever
        start = time.time()
        while len(algs_to_drill) >= frequency:
            # scramble = get_scrambles.gen_premove(20, 25)
            scramble = get_scramble.gen_premove(10, 15)
            cube = Memo(scramble, can_parity_swap=True, ls=self.cube_memo.ls)
            edge_memo = cube.format_edge_memo(cube.memo_edges()).split(" ")
            no_cycle_break_edge_memo = set()
            last_added_pair = ""
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
            if (
                last_added_pair in algs_to_drill
                and (len(cube.flipped_edges) // 2) % 2 == 1
            ):
                continue

            algs_in_scramble = algs_to_drill.intersection(no_cycle_break_edge_memo)
            if len(algs_in_scramble) >= frequency:
                if not return_list:
                    number += 1
                    print(f"Scramble {number}/{len_algs_to_drill}:", scramble)
                    # todo make it so if you're no_repeat then allow to repeat the letter pairs
                    response = input('Enter "r" to repeat letter pairs: ')
                    if response == "m":
                        Solution(
                            scramble, buffer_order=self.cube_memo.buffer_order
                        ).display()
                        scrambles.append(scramble)
                        response = input('Enter "r" to repeat letter pair(s): ')

                    if response != "r" and no_repeat:
                        algs_to_drill = algs_to_drill.difference(algs_in_scramble)
                    print()
                    start = time.time()
                    if response == "q" or response == "quit":
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
            print("Now reducing scramble")
        start = time.time()

        reduced_scramble = self.cube_memo.get_solution(
            max_depth=min(len(scramble.split()), 20)
        )

        end = time.time()
        if disp_time_taken:
            print(f"Time: {end - start:.3f}")
            print("--------______---------")
            print("Done")

        # print(len(scramble.split()), len(reduced_scramble.split()))
        return self.cube_memo.invert_solution(reduced_scramble)

    def remove_piece(self, target_list, piece):
        piece_adj1, piece_adj2 = self.cube_memo.adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    # memo
    def generate_random_pair(self, target_list):
        first = random.choice(target_list)
        self.remove_piece(target_list, first)
        second = random.choice(target_list)
        return first + second

    def get_all_buffer_targets(self, buffer, piece_type="is this really needed idk"):
        if piece_type == "corners":
            corner_buffer = buffer
            corners = self.cube_memo.remove_irrelevant_corner_buffers(
                self.cube_memo.adj_corners.copy(), corner_buffer
            )
            all_corners = set(
                i + j
                for i, j in itertools.permutations(corners, 2)
                if i != self.cube_memo.adj_corners[j][0]
                and i != self.cube_memo.adj_corners[j][1]
            )
            return all_corners
        elif piece_type == "edges":
            edge_buffer = buffer
            edges = self.cube_memo.remove_irrelevant_edge_buffers(
                self.cube_memo.adj_edges, edge_buffer
            )

            all_edges = set(
                i + j
                for i, j in itertools.permutations(edges, 2)
                if i != self.cube_memo.adj_edges[j]
            )
            return all_edges
        else:
            raise Exception('put "corners" or "edges" in params pls')

    def drill_ltct(self, args):
        algs = []
        ltct_u = [
            "U R U R2' D' R U R' D R2 U2' R'",
            "R' D' R U R' D R2 U' R' U R U R' U' R U R' U",
            "U' R' U2 R U R2' D' R U R' D R2 U2'",
            "U R U R' U R2 D R' U' R D' R' U' R'",
            "R' D R' U R D' R' U R2 U' R2' U' R2 U'",
            "U R' D' R U R' D R2 U R' U2 R U R' U'",
            "R2 U R' D' R U R' D R' U' R2 U' R2' U'",
            "D R2' U' R U R U' R D' U R U' R' U",
            "U R' D' R U' R' D R U2 R U R' U2 R U R' U'",
            "U' R' U2 R U R2' F' R U R U' R' F R U'",
            "U' f R' F' R U2 R U2' R' U2 S'",
            "U R' U R U R' U' R' D' R U' R' D R2",
            "U' R2 D R' U' R D' R' U' R' U R U R' U2",
            "U R U R' U2 L U' R U L' U R'",
            "U2' R' U2 L U' R U L' U R' U R U'",
            "R' U' R U D' R U' R U R U' R2' D U",
            "U R U R' U' R U R2' D' R U2 R' D R2 U2' R' U",
            "U' R' U' R U R' U' R2 D R' U R D' R' U2 R' U R U'",
            "U' R D R' U' R D' R2' U R U' R' U' R U R' U' R",
            "U2 R' U' R2 D R' U' R D' R2' U2' R U",
            "R U R D R' U R D' R2' U' R U' R' U'",
            "U' R U' R' U R U' R' U' R U R2' D' R U' R' D R",
            "U R U' R' U2 R U' R2' D' R U' R' D R U'",
            "R U2 R' U' R2 D R' U' R D' R2' U'",
            "D' U R2 D' R U R' D R2 U R' U2 R D",
            "R2' D' R U R' D R U R U' R' U' R U'",
            "U R' F' R U R' U' R' F R2 U' R' U2 R U",
            "R U R' U' R U R2' D' R U' R' D R U2 R U' R' U2",
            "U R U2' R' U' F' R U R' U' R' F R2 U' R'",
            "U' R U R' U' R' U R' U' D R' U R D' R",
            "U R U' R' U2 R U' R' U2 R' D' R U R' D R U'",
            "U R' U' R U2 R D R' U' R D' R2' U R U' R' U R U",
            "D' U' R2 U R' U' R' U R' U' D R' U R",
            "U2 R U' R' U' R U R D R' U R D' R2' U",
            "U' R' U L' U R2 U R2' U R2 U2' R' L",
            "U2 R2 D' r U2 r' D R U2 R U'",
            "U' L' U' L U' R U' L' U R' U2' L",
        ]
        # TODO: this list is not complete
        ltct_ud = [
            "U R D R' U R D' R2' U R U2 R' U R U'",
            "R D R' U R D' R2' U R U R' U2' R",
            "D U R2 D' R U R' D R2 U R' U2 R D'",
            "D R' U2 R U' R2 D' R U' R' D R2 U' D'",
            "D U R' U' R U2 R' U' R2 D R' U' R D' R' U' D'",
            "R' U2 R U' R2 D' R U' R' D R2 U'",
            "U R' U' R U2 R' U' R2 D R' U' R D' R' U'",
            "D' R' U2 R U' R2 D' R U' R' D R2 U' D",
            "D' U R' U' R U2 R' U' R2 D R' U' R D' R' U' D",
        ]

        if "-u" in args:
            algs += ltct_u
        if "-ud" in args:
            algs += ltct_ud
        if "-def" in args:
            algs += ltct_u + ltct_ud

        self.drill_algs(algs)

    def drill_ltct_scramble(self):
        # we are now going to pretent that we know what we are dioing
        # todo this is where drill ltct goes
        # todo add args for which LTCTs are filtered for
        while True:
            while True:
                # get parity scramble
                scramble = get_scramble.get_scramble(requires_parity=True)
                self.cube_memo = Memo(scramble)
                twisted_corners = self.cube_memo.twisted_corners
                twisted_corner_count = self.cube_memo.twisted_corners_count
                corner_memo = self.cube_memo.memo_corners()
                # check last parity target
                if (
                    twisted_corner_count == 1
                    and "U" in corner_memo.pop()
                    and "U" in next(iter(twisted_corners.values()))
                ):
                    break
            print(scramble, end="")
            response = input()
            if response in ("q", "quit"):
                return

    def parallel_cancel(self, pre_move: list, solution: list):
        sol = solution.copy()
        pre_move_len = len(pre_move)

        solution = pre_move + solution
        # todo figure out why this is needed
        # post_move = "F' D2 R'"
        # k_sol = "R D2 F2 R2 F' U' B U' B U' L2 F2 U' R2 U F2 D' L2 U'"
        if "" in solution:
            solution.remove("")
        opp = {
            "U": "D",
            "D": "U",
            "F": "B",
            "B": "F",
            "L": "R",
            "R": "L",
        }
        for i in range(len(solution) - 3):
            if DEBUG:
                print("SOLUTION", solution)
            first_layer = solution[i][0]
            first_turn = solution[i]
            second_layer = solution[i + 1][0]
            third_layer = solution[i + 2][0]
            third_turn = solution[i + 2]
            if first_layer == third_layer and first_layer == opp[second_layer]:
                canceled_cube = Cube(first_turn + " " + third_turn)
                # todo convert to using combined rotation and simplifying
                kociemba_solution = canceled_cube.solve(invert=True).split()
                if DEBUG:
                    print("k sol", kociemba_solution)

                if i < pre_move_len:
                    pre_move[i] = " ".join(kociemba_solution)
                if i + 2 < pre_move_len:
                    pre_move[i + 2] = ""

                if i >= pre_move_len:
                    sol[i - pre_move_len] = kociemba_solution
                if i + 2 >= pre_move_len:
                    sol[i + 2 - pre_move_len] = ""
                if DEBUG:
                    print(pre_move)
                if DEBUG:
                    print(solution)
                if "" in pre_move:
                    pre_move.remove("")
                if "" in sol:
                    sol.remove("")

                return self.parallel_cancel(pre_move, sol)
                # kociemba_solution

        return pre_move, sol

    def cancel(self, pre_move, solution):
        # todo find a way to also cancel U D U moves
        # aka check for parallel cancellations
        solution = solution.rstrip("\n").strip().split(" ")[:]
        pre_move = pre_move.rstrip("\n").strip().split(" ")[:]
        # checking for parallel cancel
        pre_move, solution = self.parallel_cancel(pre_move, solution)
        rev_premove = pre_move[::-1]
        if DEBUG:
            print(solution, pre_move, rev_premove, sep=" || ")
        solved = Cube()

        # full vs partial cancel

        # calculate cancel type
        for depth, (pre, s) in enumerate(zip(rev_premove.copy(), solution.copy())):
            combined = pre + " " + s
            canceled_cube = Cube(combined)

            if DEBUG:
                print(
                    pre,
                    "||",
                    s,
                    "Full cancel:",
                    "nope" if solved != canceled_cube else "yep",
                )

            if not pre or not s:
                break

            if DEBUG:
                print(
                    pre, "||", s, "Parital cancel:", "nope" if pre[0] != s[0] else "yep"
                )

            if solved == canceled_cube and depth < 1:
                # full cancel
                # remove the two canceled moves and recurse
                if DEBUG:
                    print("recursing")
                rev_premove.remove(pre)
                solution.remove(s)
                if DEBUG:
                    print(solution, rev_premove, sep=" || ")

                return self.cancel(" ".join(rev_premove[::-1]), " ".join(solution))

            # partial cancel
            elif pre[0] == s[0] and depth < 1:
                canceled_cube = Cube(pre + " " + s)
                # todo convert to using combined rotation and simplifying
                kociemba_solution = canceled_cube.solve(invert=True).split()
                if DEBUG:
                    print("k sol", kociemba_solution)

                # kociemba_solution
                if DEBUG:
                    print(rev_premove)
                rev_premove.remove(pre)
                solution.remove(s)
                solution = kociemba_solution + solution
                return self.cancel(" ".join(rev_premove[::-1]), " ".join(solution))
            break
        if DEBUG:
            print(
                "Returning", " ".join(rev_premove[::-1]), " ".join(solution), sep=" || "
            )
        return " ".join(rev_premove[::-1]) + " " + " ".join(solution).strip()

    @staticmethod
    def _get_twists():
        twists = {
            "CW": {
                "UBL": "R U R D R' D' R D R' U' R D' R' D R D' R2",
                "UBR": "R D R' D' R D R' U' R D' R' D R D' R' U",
                "UFL": "U' R' D R D' R' D R U R' D' R D R' D' R",
                "DFL": "U R U' R' D R U R' U' R U R' D' R U' R'",
                "DFR": "D' U' R' D R U R' D' R D R' D' R U' R' D R U",
                "DBR": "U R U' R' D' R U R' U' R U R' D R U' R'",
                "DBL": "D' R D R' U' R D' R' D R D' R' U R D R'",
            },
            "CCW": {
                "UBL": "R2 D R' D' R D R' U R D' R' D R D' R' U' R'",
                "UBR": "U' R D R' D' R D R' U R D' R' D R D' R'",
                "UFL": "R' D R D' R' D R U' R' D' R D R' D' R U",
                "DFL": "R U R' D R U' R' U R U' R' D' R U R' U'",
                "DFR": "U' R' D' R U R' D R D' R' D R U' R' D' R U D",
                "DBR": "R U R' D' R U' R' U R U' R' D R U R' U'",
                "DBL": "R D' R' U' R D R' D' R D R' U R D' R' D",
            },
        }
        return twists

    def drill_twists(self, mode):
        """2f: floating 2-twist, 3: 3-twist, or 3f: floating 3-twist"""
        twists = self._get_twists()
        if mode == "3":
            cw_twists = twists["CW"].values()
            ccw_twists = twists["CCW"].values()
            cw = list(itertools.combinations(cw_twists, r=2))
            ccw = list(itertools.combinations(ccw_twists, r=2))
            algs = [a + " " + b for (a, b) in cw + ccw]

        elif mode == "3f":
            cw_twists = twists["CW"].values()
            ccw_twists = twists["CCW"].values()
            cw = list(itertools.combinations(cw_twists, r=3))
            ccw = list(itertools.combinations(ccw_twists, r=3))
            algs = [a + " " + b + " " + c for (a, b, c) in cw + ccw]

        elif mode == "2f" or mode == "2":
            cw_twists = twists["CW"].values()
            ccw_twists = twists["CCW"].values()

            algs = []
            for cw_twist, ccw_twist in itertools.product(cw_twists, ccw_twists):
                if not Cube(cw_twist + " " + ccw_twist).is_solved():
                    algs.append(cw_twist + " " + ccw_twist)

            algs.extend(itertools.chain(cw_twists, ccw_twists))
        else:
            print("Twist pattern not recognized")
            return

        self.drill_algs(algs)

    def drill_algs(self, algs):
        algs_help_num = 0
        algs_help = []

        last_solution = None
        no_repeat = True
        num = 1
        len_algs = len(algs)
        # TODO support wide moves
        while algs:

            if DEBUG:
                print("getting random alg...")
            alg = a = random.choice(algs)

            post_move = self.gen_premove()
            if DEBUG:
                print(post_move)

            alg_with_post_move = alg + " " + post_move
            cube = Cube(alg_with_post_move)
            if DEBUG:
                print("kociemba solving...")

            k_sol = cube.solve(max_depth=16)

            if DEBUG:
                print("//", post_move, "||", k_sol)
                print("SETUP:", post_move, alg_with_post_move, sep=" || ")
                print("canceling")

            solution = self.cancel(post_move, k_sol)

            if len(solution.split()) > 25:
                if DEBUG:
                    print(f"Long solution {len(solution.split())}:")
                    continue

            if no_repeat:
                algs.remove(alg)

            if DEBUG:
                print("at input...")
            if last_solution != solution:
                print(f"Num {num}/{len_algs}:", solution)
                num += 1
                last_solution = solution
                response = input("")
                if response == "q" or response == "quit":
                    return
                elif response.startswith("a"):
                    print("Alg:", a, "\n")
                    algs_help_num += 1
                    algs_help.append(a)
        print(algs_help_num, algs_help)

    def gen_premove(self, min_len=1, max_len=3, requires_parity=False):
        faces = ["U", "L", "F", "R", "B", "D"]
        directions = ["", "'", "2"]
        turns = []
        if max_len < 1:
            raise ValueError("max_len must be greater than 0")
        if min_len > max_len:
            raise ValueError("min_len cannot be greater than max len")
        scram_len = random.randint(min_len, max_len)
        opp = {
            "U": "D",
            "D": "U",
            "F": "B",
            "B": "F",
            "L": "R",
            "R": "L",
        }

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

        joined_scramble = " ".join(scramble)

        has_parity = (len(scramble) - joined_scramble.count("2")) % 2 == 1

        if not requires_parity:
            return joined_scramble

        if requires_parity and not has_parity:
            return self.gen_premove(
                min_len=min_len, max_len=max_len, requires_parity=requires_parity
            )
        if requires_parity and has_parity:
            return joined_scramble

    def cycle_break_float(self, buffer, buffer_order=None):
        """Syntax: cbuff <buffer>
        Desc: provides scrambles with flips/twists and cycle breaks to practice all edge and corner buffers
        Aliases:
            m"""
        piece_type = "edge" if len(buffer) == 2 else "corner"

        if piece_type == "edge":
            self.cycle_break_floats_edges(buffer, buffer_order=buffer_order)
        elif piece_type == "corner":
            self.cycle_break_floats_corners(buffer, buffer_order=buffer_order)

    def cycle_break_floats_edges(self, buffer, buffer_order=None):
        """Syntax: cbuff <edge buffer>
        Desc: provides scrambles with flips and cycle breaks to practice all edge buffers
        """
        allow_other_floats = False

        while True:
            drill = Drill(buffer_order=buffer_order)
            scram = drill.drill_edge_buffer_cycle_breaks(buffer)
            cube = Cube(scram, can_parity_swap=False)
            if buffer in cube.solved_edges or len(cube.flipped_edges) >= 4:
                continue
            cube_trace = cube.get_dlin_trace()
            flipped_count = 0
            for edge in cube_trace["edge"]:

                flipped_count += edge["orientation"] and edge["type"] == "misoriented"
                if (
                    edge["type"] == "cycle"
                    and edge["orientation"] == 0
                    and edge["parity"] == 0
                    and (edge["buffer"] == buffer or not allow_other_floats)
                ):
                    cycle_breaks = False
                    break
            else:
                cycle_breaks = True

            if flipped_count > 1:
                continue

            if cycle_breaks:
                print(scram)
                input()

    def cycle_break_floats_corners(self, buffer, buffer_order=None):
        """Syntax: cbuff <corner buffer>
        Desc: provides scrambles with twists and cycle breaks to practice all corner buffers
        """
        allow_other_floats = False
        while True:
            drill = Drill(buffer_order=buffer_order)
            scram = drill.drill_corner_buffer_cycle_breaks(buffer)
            cube = Cube(scram, can_parity_swap=False)
            if buffer in cube.solved_corners or len(cube.twisted_corners) > 3:
                continue
            cube_trace = cube.get_dlin_trace()
            for corner in cube_trace["corner"]:

                if (
                    corner["type"] == "cycle"
                    and corner["orientation"] == 0
                    and corner["parity"] == 0
                    and (corner["buffer"] == buffer or not allow_other_floats)
                ):
                    cycle_breaks = False
                    break
            else:
                cycle_breaks = True

            if cycle_breaks:
                print(scram)
                input()

    def drill_two_flips(self):
        two_flips = {
            "[U , R' E2 R2 E' R']": "U R' E2 R2 E' R' U' R E R2' E2' R",
            "[U' : [S , R' F' R]] [U2' , M']": "U' S R' F' R S' R' F R U' M' U2 M",
            "[U' , L E2' L2' E L]": "U' L E2' L2' E L U L' E' L2 E2 L'",
            "[L' E2' L , U'] [U' , L E' L']": "L' E2' L U' L' E2 L2 E' L' U L E L'",
            "[R E2 R' , U] [U , R' E R]": "R E2 R' U R E2' R2' E R U' R' E' R",
            "[R' E2 R , U] [U , R E' R']": "R' E2 R U R' E2' R2 E' R' U' R E R'",
            "[L E2' L' , U'] [U' , L' E L]": "L E2' L' U' L E2 L2' E L U L' E' L",
            "[M' , U2] [U : [S , R' F' R]]": "M' U2 M U' S R' F' R S' R' F R U'",
            "[U' : [R E R' , U2]] [U : [S , R2']]": "U' R E R' U2 R E' R' S R2' S' R2 U'",
            "[M U' : [S , R' F' R]] [M , U2]": "M U' S R' F' R S' R' F R U' M' U2'",
            "[U : [L' E' L , U2']] [U' : [S' , L2]]": "U L' E' L U2' L' E L S' L2 S L2' U",
            "[R' E2 R2 E' R' , U']": "R' E2 R2 E' R' U' R E R2' E2' R U",
            "[S , R' F' R] [U' : [M' , U2]]": "S R' F' R S' R' F R U' M' U2 M U'",
            "[U R : [U' , R' E' R2 E2 R']]": "U R U' R' E' R2 E2 R' U R E2' R2' E U'",
            "[U , R' E R] [R E2 R' , U]": "U R' E R U' R' E' R2 E2 R' U R E2' R' U'",
            "[R E' R2' : [F2 , R S' R']] [R : [E' , R2']]": "R E' R2' F2 R S' R' F2' R S R' E R",
            "[U : [L' E L , U]] [U2 : [L E2' L' , U']]": "U L' E L U L' E' L2 E2' L' U' L E2 L' U'",
            "[U' : [M' , U2]] [S , R' F' R]": "U' M' U2 M U' S R' F' R S' R' F R",
            "[R' F' R , S'] [S' U' : [M' , U2]]": "R' F' R S' R' F R U' M' U2 M U' S",
            "[U' M U' : [S , R' F' R]] [U' : [M , U2]]": "U' M U' S R' F' R S' R' F R U' M' U'",
            "[R2' , S'] [S' : [U2 , R E R']]": "R2' S' R2 U2 R E R' U2' R E' R' S",
            "[L E2' L2' E L , U]": "L E2' L2' E L U L' E' L2 E2 L' U'",
            "[L E' L' , U] [U , L' E2' L]": "L E' L' U L E L2' E2' L U' L' E2 L",
            "[R' E R , U'] [U' , R E2 R']": "R' E R U' R' E' R2 E2 R' U R E2' R'",
            "[R E' R' , U'] [U' , R' E2 R]": "R E' R' U' R E R2' E2 R U R' E2' R",
            "[L' E L , U] [U , L E2' L']": "L' E L U L' E' L2 E2' L' U' L E2 L'",
            "[U2 , M'] [U' : [S , R' F' R]]": "U2 M' U2' M U' S R' F' R S' R' F R U",
            "[U : [R E R' , U2]] [U' : [S , R2']]": "U R E R' U2 R E' R' S R2' S' R2 U",
            "[U2 M U' : [S , R' F' R]] [U2 , M]": "U2 M U' S R' F' R S' R' F R U' M'",
            "[U' : [L' E' L , U2']] [U : [S' , L2']]": "U' L' E' L U2' L' E L S' L2' S L2 U'",
            "[U' , L E' L'] [L' E2' L , U']": "U' L E' L' U L E L2' E2' L U' L' E2 L U",
            "[U' : [R' E R , U']] [U2' : [R E2 R' , U]]": "U' R' E R U' R' E' R2 E2 R' U R E2' R' U",
            "[U' : [R E' R' , U']] [U2' : [R' E2 R , U]]": "U' R E' R' U' R E R2' E2 R U R' E2' R U",
            "[L' E L2 : [F2' , L' S L]] [L' : [E , L2]]": "L' E L2 F2' L' S L F2 L' S' L E' L'",
            "[U : [M' , U2']] [S' , L F L']": "U M' U2' M U S' L F L' S L F' L'",
            "[S , R2'] [U2 , R E R']": "S R2' S' R2 U2 R E R' U2' R E' R'",
            "[U M U' : [S , R' F' R]] [U : [M , U2']]": "U M U' S R' F' R S' R' F R U' M' U",
            "[L F L' , S] [S U : [M' , U2']]": "L F L' S L F' L' U M' U2' M U S'",
            "[R S R' F2 : [R2 , E]] [R S R' , F2]": "R S R' F2 R2 E R2' E' R S' R' F2'",
            "[R2 , E'] [E' : [F2 , R S' R']]": "R2 E' R2' F2 R S' R' F2' R S R' E",
            "[R2 , E] [R S' R' , F2]": "R2 E R2' E' R S' R' F2 R S R' F2'",
            "[R U' : [M' , U2]] [R S R' , F']": "R U' M' U2 M U' S R' F' R S' R' F",
            "[S L : [E' , L2']] [r , E' L' E]": "S L E' L2' E L S' r E' L' E r' E' L E",
            "[M : [L' E2' L , U']] [M : [U' , L E' L']]": "M L' E2' L U' L' E2 L2 E' L' U L E L' M'",
            "[L : [E' , L2']] [L F2' L' , S]": "L E' L2' E L2 F2' L' S L F2 L' S'",
            "[L2' , E'] [L' S L , F2']": "L2' E' L2 E L' S L F2' L' S' L F2",
            "[E , R2] [F2 , R S' R']": "E R2 E' R2' F2 R S' R' F2' R S R'",
            "[M' : [R' E R , U']] [M' : [U' , R E2 R']]": "M' R' E R U' R' E' R2 E2 R' U R E2' R' M",
            "[R' : [E , R2]] [R' F2 R , S']": "R' E R2 E' R2' F2 R S' R' F2' R S",
            "[M : [R E2 R' , U]] [M : [U , R' E R]]": "M R E2 R' U R E2' R2' E R U' R' E' R M'",
            "[S' R' : [E , R2]] [l' , E R E']": "S' R' E R2 E' R' S l' E R E' l E R' E'",
            "[R2' , E'] [E' R' : [S' , R' F2 R]]": "R2' E' R S' R' F2 R S R' F2' R2 E",
            "[r : [E' , R' U' R]] [M' : [U' , R' E2 R]]": "r E' R' U' R E R' U R r' M' U' R' E2 R U R' E2' R M",
            "[l : [S , R2']] [l U2 l' , S']": "l S R2' S' R2 U2 l' S' l U2' l' S",
            "[r' : [E2 , R U R']] [M : [U , R E' R']]": "r' E2 R U R' E2' R U' R' r M U R E' R' U' R E R' M'",
            "[S' R : [E' , R2']] [l , E' R' E]": "S' R E' R2' E R S l E' R' E l' E' R E",
            "[R' U' : [M' , U2]] [R' : [S , R' F' R]]": "R' U' M' U2 M U' S R' F' R S' R' F R2",
            "[S L' : [E , L2]] [r' , E L E']": "S L' E L2 E' L' S' r' E L E' r E L' E'",
            "[l : [E2' , L' U' L]] [M : [U' , L' E L]]": "l E2' L' U' L E2 L' U L l' M U' L' E L U L' E' L M'",
            "[r' : [S' , L2]] [r' U2' r , S]": "r' S' L2 S L2' U2' r S r' U2 r S'",
            "[S , R F' R'] [S' , R' F' R]": "S R F' R' S' R F R' S' R' F' R S R' F R",
            "[M2 U' : [S , R' F' R]] [M2 : [U2 , M']]": "M2 U' S R' F' R S' R' F R U' M' U2' M'",
            "[S' , L' F L] [S , L F L']": "S' L' F L S L' F' L S L F L' S' L F' L'",
            "[S2' , r' U' r] [r' : [U' , L' E L]]": "S2' r' U' r S2 r' L' E L U L' E' L r",
            "[U' : [R2' , S']] [R F R' , S']": "U' R2' S' R2 S U R F R' S' R F' R' S",
            "[S2 , l U l'] [l : [U , R E' R']]": "S2 l U l' S2' l R E' R' U' R E R' l'",
        }
        algs = list(two_flips.values())
        random.shuffle(algs)
        self.drill_algs(algs)


if __name__ == "__main__":
    # todo add translate UR to B and B to UR function

    drill = Drill()
    s = drill.drill_edge_buffer_cycle_breaks("UB")
    print(s)
