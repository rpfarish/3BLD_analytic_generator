from Cube.memo import Memo
from Cube.solution import Solution
from Scramble import get_scramble


def memo_cube(scramble):
    s = Solution(scramble)
    solution = s.get_solution()

    print("Can float edges:", s.can_float_edges)
    print("Scramble", scramble)
    print(f"Parity:", solution["parity"])
    print(f"Edges:", solution["edges"])
    print(f"Flipped Edges:", solution["flipped_edges"])
    print("Edge Buffers:", solution["edge_buffers"])
    print("Corners:", solution["corners"])
    print("Twisted Corners:", cube.twisted_corners)
    print("Alg count:", solution["number_of_algs"])
    corner_memo = solution["corners"]
    print(corner_memo)
    # no_cycle_break_corner_memo = set()
    corner_buffers = solution["corner_buffers"]
    print(corner_buffers)


# algs_to_drill = {'EB', 'ZV', 'VZ', 'ZO', 'FA', 'SB', 'BV', 'CD', 'NM', 'AV', 'FL'}
all_edges = {
    "UB",
    "UR",
    "UL",
    "LU",
    "LF",
    "LD",
    "LB",
    "FR",
    "FD",
    "FL",
    "RU",
    "RB",
    "RD",
    "RF",
    "BU",
    "BL",
    "BD",
    "BR",
    "DF",
    "DR",
    "DB",
    "DL",
}

sticker_to_drill = "DB"
adj = sticker_to_drill[::-1]
all_edges.remove(sticker_to_drill)
all_edges.remove(adj)
invert_pairs = False
if invert_pairs:
    algs_to_drill = {i + sticker_to_drill for i in all_edges}
else:
    algs_to_drill = {sticker_to_drill + i for i in all_edges}

# algs_to_drill = {''}
print(algs_to_drill)
# algs_to_drill = algs_to_drill.union({"UBDF", "URRD", "ULLD"})
# print(algs_to_drill)
number = 0
# print(len(algs_to_drill))
print("This program generates scrambles that contain certain letter pairs")
frequency = int(input("Enter freq (recommended less than 3): "))
no_cycle_break_edge_memo = set()
# print('Running...')
# algs_to_drill = {"LFFD"}
strict = True
no_repeat = True
# I don't recommend going above 2 else it will take forever
while len(algs_to_drill) >= frequency:
    scramble = get_scramble.gen_premove(min_len=17, max_len=20)
    cube = Memo(scramble, can_parity_swap=True)
    edge_memo = cube.format_edge_memo(cube.memo_edges()).split(" ")
    last_added_pair = ""
    # print(scramble)
    no_cycle_break_edge_memo = set(edge_memo)

    if strict:
        no_cycle_break_edge_memo.clear()
        edge_buffers = cube.edge_memo_buffers
        for pair in edge_memo:
            pair_len_half = len(pair) // 2
            a = pair[:pair_len_half]
            b = pair[pair_len_half:]

            if a in edge_buffers or b in edge_buffers:
                break
            last_added_pair = pair
            no_cycle_break_edge_memo.add(pair)

    if last_added_pair in algs_to_drill and (len(cube.flipped_edges) // 2) % 2 == 1:
        continue

    algs_in_scramble = algs_to_drill.intersection(no_cycle_break_edge_memo)

    if len(algs_in_scramble) >= frequency:
        print("Scramble:", scramble)
        # todo make it so if you're no_repeat then allow to repeat the letter pairs
        response = input('Enter "r" to repeat letter pairs: ')

        if response == "m":
            memo_cube(scramble)
            response = input('Enter "r" to repeat letter pairs: ')

        if response == "r":
            pass
        elif no_repeat or False:
            algs_to_drill = algs_to_drill.difference(algs_in_scramble)

        print()
