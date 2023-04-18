import get_scrambles
from Cube.cube import Cube
from Cube.letterscheme import letter_scheme, LetterScheme


def remove_piece(target_list, piece, ltr_scheme):
    piece_adj1, piece_adj2 = Cube(ls=ltr_scheme).adj_corners[piece]
    target_list.remove(piece)
    target_list.remove(piece_adj1)
    target_list.remove(piece_adj2)
    return target_list


def generate_random_pair(target_list, ltr_scheme):
    import random
    first = random.choice(target_list)
    remove_piece(target_list, first, ltr_scheme)
    second = random.choice(target_list)
    return first + second


def generate_drill_list(piece_type, ltr_scheme: LetterScheme, buffer, target):
    # pick what letter scheme to use
    # how to separate c from e
    # just doing corners first
    all_targets = LetterScheme(use_default=False).get_edges()
    remove_piece(all_targets, buffer, ltr_scheme)

    # random_list = []
    # # generate random pair
    # for _ in range(18):
    #     target_list = all_targets[:]
    #     random_list.append(generate_random_pair(target_list, ltr_scheme))

    target_list = all_targets[:]
    # remove buffer stickers
    remove_piece(target_list, target, ltr_scheme)

    # generate random pairs
    # generate specific pairs
    # generate target groups e.g. just Z or H and k
    # generate inverse target groups
    # specify buffer
    return {target + i for i in target_list}


sticker_to_drill = "L"

algs_to_drill = generate_drill_list('c', letter_scheme, "U", sticker_to_drill)
number = 0
algs_to_drill = {"NS"}
alg_freq_dist = {str(pair): 0 for pair in algs_to_drill}
print(type(alg_freq_dist))
print('Running...')
count = 2
inc_amt = 2
while True:
    scramble = get_scrambles.get_scramble()
    cube = Cube(scramble, ls=letter_scheme)
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
        # print(max(alg_freq_dist.values()),  min(alg_freq_dist.values()), max(alg_freq_dist.values())-min(alg_freq_dist.values()))

        alg_to_drill = alg_to_drill.pop()
        # check if freq is < count and if so continue
        if alg_freq_dist[alg_to_drill] < count:
            alg_freq_dist[alg_to_drill] += 1
        elif len(set(alg_freq_dist.values())) == 1:
            count += inc_amt
        else:
            continue

        # print(alg_to_drill)
        # print(alg_freq_dist, sep="")
        # print(corner_memo)
        # print(no_cycle_break_corner_memo)
        print(Cube().reduce_scramble(scramble))
        input()
