"""Finds letter pairs from cube scrambles"""

from Cube.cube import Cube

from solution import Solution

scramble_file = "scrambles.txt"


# TODO support wide moves
# TODO return twists with top or bottom color
# TODO add alg count

def main():
    # data = get_all()
    with open(scramble_file) as f:
        for number, scramble in enumerate(f.readlines(), 1):
            print("Solve Number:", number)
            number += 1
            scramble = "F2 D2 R' D2 F2 R2 U2 B2 L2 R B' U' R F' D R U' B' D' L"
            cube = Cube(scramble, can_parity_swap=True)
            s = Solution(scramble, )
            solution = s.get_solution()

            print("Can float edges:", s.can_float_edges)
            print("Scramble", scramble)
            print(f"Parity:", solution['parity'])
            print(f"Edges:", solution['edges'])
            print(f"Flipped Edges:", solution['flipped_edges'])
            print("Edge Buffers:", solution['edge_buffers'])
            # _sum = 0
            # for i in edge_memo:
            #     _sum += data[i]
            # print(_sum)

            print("Corners:", solution['corners'])
            print("Twisted Corners:", cube.twisted_corners)
            print("Alg count:", solution['number_of_algs'])
            corner_memo = solution['corners']
            print(corner_memo)
            no_cycle_break_corner_memo = set()
            corner_buffers = solution['corner_buffers']
            print(corner_buffers)
            for pair in corner_memo:
                print(pair)
                if len(pair) == 6:
                    a = pair[:3]
                    b = pair[3:]
                elif len(pair) == 3:
                    a = pair
                    b = ''
                if a in corner_buffers or b in corner_buffers:
                    break
                no_cycle_break_corner_memo.add(pair)
            print(s.edge_float_buffers)
            print(cube.memo_edges())
            print("corner memo before cycle breaks", no_cycle_break_corner_memo)
            print("\n")
            break

# make ui
# todo finish importing database letter pairs
# TODO give options to memo floats and auto solve flipped edges into the memo
# todo create a context manager to add to each method
# all computers do is reduce the space of a problem down to something that they can just search through completely


if __name__ == '__main__':
    main()
