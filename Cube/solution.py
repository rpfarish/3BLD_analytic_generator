from pprint import pprint

import dlin
from Cube.dlin_float import find_optimal_combinations
from Cube.memo import Memo


class Solution:
    def __init__(
        self,
        scramble,
        settings,
        inc_floats=True,
    ):
        self.cube = Memo(
            scramble,
            auto_scramble=False,
            can_parity_swap=True,
            ls=settings.letter_scheme,
            buffers=settings.buffers,
            parity_swap_edges=settings.parity_swap_edges,
            buffer_order=settings.buffer_order,
        )
        self.scramble = scramble
        self.parity = self.cube.has_parity
        self.cube.scramble_cube(self.scramble)

        self.buffers = settings.buffers
        self.buffer_order = settings.buffer_order
        self.settings: Settings = settings

        self.edges = self.cube.format_edge_memo(self.cube.memo_edges()).split(" ")
        self.flipped_edges = list(self.cube.flipped_edges)
        self.edge_buffers = list(self.cube.edge_memo_buffers)

        self.corners = self.cube.format_corner_memo(self.cube.memo_corners()).split(" ")
        self.twisted_corners = list(self.cube.twisted_corners)
        self.corner_buffers = list(self.cube.corner_memo_buffers)
        self.can_float_corners = None

        if settings.parity_swap_edges is not None:
            self.parity_swap_edges = tuple(settings.parity_swap_edges.split("-"))
        else:
            self.parity_swap_edges = None

        self.number_of_edge_flips = len(self.flipped_edges) // 2
        self.number_of_corner_twists = len(self.twisted_corners) // 3
        self.number_of_algs = self.count_number_of_algs(inc_floats=inc_floats)
        self.edge_float_buffers = []
        # FIX: rename this

        self.inc_floats = inc_floats
        # TODO: support wide moves

        # TODO: return twists with top or bottom color
        # TODO: add alg count

    @property
    def can_float_edges(self) -> bool:
        trace = self.get_dlin_trace()

        results = find_optimal_combinations(trace["edge"], self.buffer_order)

        buffer_count = [group for group in results if group["target_count"] != 0]
        return len(buffer_count) >= 2 or not any(
            self.buffers["edge_buffer"] in t["buffers"] for t in results
        )

    def get_float_memo(self):
        if self.can_float_edges:
            return "floating edge memo"

    def get_dlin_trace(self):
        if self.parity:
            swap = self.parity_swap_edges
        else:
            swap = None

        return dlin.trace(
            scramble=self.scramble, swap=swap, buffers=self.settings.dlin_buffers
        )

    def count_sandwich_floats(self):
        dlin_trace = self.get_dlin_trace()
        float_count = 0
        for buffer_trace in dlin_trace["corner"] + dlin_trace["edge"]:
            float_count += (
                buffer_trace["orientation"] == 0
                and buffer_trace["parity"] == 0
                and buffer_trace["type"] == "cycle"
                and buffer_trace["buffer"] not in self.buffers.values()
            )

        return float_count

    def count_number_of_algs(self, inc_floats=True) -> int:
        number_of_floats = self.count_sandwich_floats() if inc_floats else 0

        twists_to_alg = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
        flips_to_alg = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
        # print(self.edges, len(self.edges), self.corners, len(self.corners), "FLIPS", self.number_of_edge_flips,
        #       "TWISTS", self.number_of_corner_twists, "FLOATS", number_of_floats)
        # Debug print statements for num_of_algs calculation
        # print(f"DEBUG: len(self.edges) = {len(self.edges)}")
        # print(f"DEBUG: len(self.corners) = {len(self.corners)}")
        # print(f"DEBUG: self.number_of_edge_flips = {self.number_of_edge_flips}")
        # print(
        #     f"DEBUG: flips_to_alg.get({self.number_of_edge_flips}, {self.number_of_edge_flips}) = {flips_to_alg.get(self.number_of_edge_flips, self.number_of_edge_flips)}"
        # )
        # print(f"DEBUG: self.number_of_corner_twists = {self.number_of_corner_twists}")
        # print(
        #     f"DEBUG: twists_to_alg.get({self.number_of_corner_twists}, {self.number_of_corner_twists // 2}) = {twists_to_alg.get(self.number_of_corner_twists, self.number_of_corner_twists // 2)}"
        # )

        # Calculate intermediate sum before subtracting floats
        algs_before_floats = (
            len(self.edges)
            + len(self.corners)
            + flips_to_alg.get(self.number_of_edge_flips, self.number_of_edge_flips)
            + twists_to_alg.get(
                self.number_of_corner_twists, self.number_of_corner_twists // 2
            )
        )
        # print(f"DEBUG: algs_before_floats = {algs_before_floats}")
        # print(f"DEBUG: number_of_floats = {number_of_floats}")

        num_of_algs = algs_before_floats - number_of_floats
        # print(f"DEBUG: final num_of_algs = {num_of_algs}")
        return num_of_algs

    def get_solution(self):
        solution = {
            "scramble": self.scramble,
            "parity": self.cube.has_parity,
            "edges": self.cube.format_edge_memo(self.cube.memo_edges()).split(" "),
            "flipped_edges": list(self.cube.flipped_edges),
            "edge_buffers": list(self.cube.edge_memo_buffers),
            "can_float_edges": self.can_float_edges,
            "edge_float_buffers": self.edge_float_buffers,
            "corners": self.cube.format_corner_memo(self.cube.memo_corners()).split(
                " "
            ),
            "twisted_corners": list(self.cube.twisted_corners),
            "corner_buffers": list(self.cube.corner_memo_buffers),
            "can_float_corners": None,
            "number_of_algs": self.count_number_of_algs(inc_floats=self.inc_floats),
            "number_of_edge_flips": self.cube.flipped_edges_count,
            "number_of_corner_twists": self.cube.twisted_corners_count,
        }

        return solution

    def display(self):
        solution = self.get_solution()
        print("=" * 20, "MEMO", "=" * 20)
        print("Scramble", self.scramble)
        print("Parity:", solution["parity"])
        print("Can float edges:", self.can_float_edges)
        print("Edges:", " ".join(solution["edges"]))
        print("Corners:", " ".join(solution["corners"]))
        print("Flipped Edges:", solution["flipped_edges"])
        print("Edge Buffers:", solution["edge_buffers"])
        print("Twisted Corners:", self.cube.twisted_corners)
        print("Alg count:", solution["number_of_algs"])
        print("Corner Buffers:", solution["corner_buffers"])
        # corner_memo = solution['corners']
        # when cube is memoed, the state of the memo should be saved when the buffer is first hit
        # no_cycle_break_corner_memo = set()

        trace = self.get_dlin_trace()

        results = find_optimal_combinations(trace["edge"], self.buffer_order)
        print("=" * 20, "Dlin combine floats", "=" * 20)
        pprint(results)
        # self.get_dlin_trace_type_count_edges(trace)

        print("=" * 20, "Dlin trace", "=" * 20)
        pprint(trace)

    def get_dlin_trace_type_count_edges(self, trace) -> dict[int, int]:
        edge_types = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for edge in trace["edge"]:
            # Check if type is misoriented
            if edge.get("type") == "misoriented":
                edge_types[4] += 1
                continue

            orientation = edge["orientation"]
            parity = edge["parity"]

            match (orientation, parity):
                case (0, 0):  # Type 0: normal cycle
                    edge_types[0] += 1
                case (0, 1):  # Type 1: odd cycle (needs odd cycle)
                    edge_types[1] += 1
                case (1, 0):  # Type 2: flipped cycle (needs flipped cycle)
                    edge_types[2] += 1
                case (1, 1):  # Type 3: both (needs both odd and flipped)
                    edge_types[3] += 1

        # print(f"Edge types count: {edge_types}")
        # Validation checks

        # sum_type_1_and_3 = edge_types[1] + edge_types[3]
        # sum_type_2_3_and_4 = edge_types[2] + edge_types[3] + edge_types[4]

        # print(
        #     f"Sum of type 1 and 3: {sum_type_1_and_3} (should be even: {sum_type_1_and_3 % 2 == 0})"
        # )
        # print(
        #     f"Sum of type 2, 3, and 4: {sum_type_2_3_and_4} (should be even: {sum_type_2_3_and_4 % 2 == 0})"
        # )

        # Overall validation

        # if sum_type_1_and_3 % 2 == 0 and sum_type_2_3_and_4 % 2 == 0:
        #     print("✓ All validation checks passed!")
        # else:
        #     print("✗ Validation failed!")
        #
        return edge_types


if __name__ == "__main__":
    from Settings.settings import Settings

    s = Settings()
    # R U' D2 F2 L' B D R2 F B2 L2 U R2 B2 D2 F2 D' L2 D2 R2 F2 L B'
    scramble = "D F' D2 L2 R' D2 F2 R' L F B R L' F' D U2 B F2 U' R", s
    scramble = "R U r'"
    s = Solution(scramble, s)
    s.cube.display_cube()
    print(s.count_number_of_algs())
