from Cube.cube import Cube


class Solution:

    def __init__(self, scramble, letter_scheme=None, buffers=None):
        self.cube = Cube(scramble, auto_scramble=False, can_parity_swap=True, ls=letter_scheme, buffers=buffers)
        self.scramble = scramble
        self.parity = self.cube.has_parity
        self.cube.scramble_cube(self.scramble)

        self.edges = self.cube.format_edge_memo(self.cube.memo_edges()).split(' ')
        self.flipped_edges = list(self.cube.flipped_edges)
        self.edge_buffers = list(self.cube.edge_memo_buffers)

        self.corners = self.cube.format_corner_memo(self.cube.memo_corners()).split(' ')
        self.twisted_corners = list(self.cube.twisted_corners)
        self.corner_buffers = list(self.cube.corner_memo_buffers)
        self.can_float_corners = None

        self.number_of_edge_flips = len(self.flipped_edges) // 2
        self.number_of_corner_twists = len(self.twisted_corners) // 3
        self.number_of_algs = self.count_number_of_algs()
        self.edge_float_buffers = []
        self.can_float_edges = self.can_float_edges()

        # TODO support wide moves

        # TODO return twists with top or bottom color
        # TODO add alg count

    def can_float_edges(self):
        """
        ca cb = 2e2e
        ca bc = can float
        ac bc = 2e2e
        ac cb = same as doing ab
        :return:
        """
        memo = self.edges
        buffers = self.edge_buffers
        flips = self.number_of_edge_flips
        # print('buffers', buffers)
        for buffer in buffers:

            is_buffer_hit = False
            buffer_hit_parity = 0

            for pair in memo:
                pair_len_half = len(pair) // 2
                a = pair[:pair_len_half]
                b = pair[pair_len_half:]

                # FF
                if buffer == a and not is_buffer_hit:
                    is_buffer_hit = True
                    buffer_hit_parity = 1
                    # print('2e2e or can not float', pair)
                # LL
                elif buffer == b and not is_buffer_hit:
                    is_buffer_hit = True
                    buffer_hit_parity = 2

                    # print('2e2e or with flipped edge', pair)
                # FL
                elif buffer == b and is_buffer_hit and buffer_hit_parity == 1:
                    self.edge_float_buffers.append(buffer)
                    # print('can float from buffer', buffer, pair)
                    return True

                # FL hit opp side edge
                if buffer == self.cube.adj_edges[b] and is_buffer_hit and buffer_hit_parity == 1:
                    # print("can float from buffer, but it's flipped", buffer, pair)
                    pass

            # print("edge_buffer_count", count)
        return 'maybe'

    """
    LL => ac bc = 2e2e - buffer:A <> B:C
    FL => ca bc = can float
    
    
    # INVALID STATE
    LF => ac cb = same as doing ab
    # INVALID METHOD
    FF => cb ca = 2e2e - buffer:B <> A:C 
    
    """

    def get_float_memo(self):
        if self.can_float_edges:
            return 'floating edge memo'

    def count_number_of_algs(self) -> int:
        number_of_floats = 0

        num = len(self.edges) + len(self.corners) + self.number_of_edge_flips + self.number_of_corner_twists
        num -= number_of_floats
        return num

    def get_solution(self):
        solution = {
            'scramble': self.scramble,
            'parity': self.cube.has_parity,
            'edges': self.cube.format_edge_memo(self.cube.memo_edges()).split(' '),
            'flipped_edges': list(self.cube.flipped_edges),
            'edge_buffers': list(self.cube.edge_memo_buffers),
            'can_float_edges': self.can_float_edges,
            'edge_float_buffers': self.edge_float_buffers,
            'corners': self.cube.format_corner_memo(self.cube.memo_corners()).split(' '),
            'twisted_corners': list(self.cube.twisted_corners),
            'corner_buffers': list(self.cube.corner_memo_buffers),
            'can_float_corners': None,
            'number_of_algs': self.count_number_of_algs(),
        }
        solution['number_of_edge_flips'] = len(solution['flipped_edges']) // 2
        solution['number_of_corner_twists'] = len(solution['twisted_corners']) // 3

        return solution

    def display(self):
        solution = self.get_solution()
        print("Can float edges:", self.can_float_edges)
        print("Scramble", self.scramble)
        print(f"Parity:", solution['parity'])
        print(f"Edges:", solution['edges'])
        print(f"Flipped Edges:", solution['flipped_edges'])
        print("Edge Buffers:", solution['edge_buffers'])
        print("Corners:", solution['corners'])
        print("Twisted Corners:", self.cube.twisted_corners)
        print("Alg count:", solution['number_of_algs'])
        corner_memo = solution['corners']
        print(corner_memo)
        # when cube is memoed, the state of the memo should be saved when the buffer is first hit
        no_cycle_break_corner_memo = set()
        corner_buffers = solution['corner_buffers']
        print(corner_buffers)
