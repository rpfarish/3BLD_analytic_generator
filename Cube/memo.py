import random
import re
from typing import Optional

import kociemba

from Cube import Cube
from Cube.letterscheme import LetterScheme
from Settings.settings import Buffers


class Memo(Cube):
    def __init__(
        self,
        scramble="",
        can_parity_swap=False,
        auto_scramble=True,
        ls: LetterScheme = None,
        buffers: Optional[Buffers] = None,
        parity_swap_edges=None,
        buffer_order=None,
    ):
        super().__init__(
            s=scramble,
            can_parity_swap=can_parity_swap,
            auto_scramble=auto_scramble,
            ls=ls,
            buffers=buffers,
            parity_swap_edges=parity_swap_edges,
            buffer_order=buffer_order,
        )

    # memo
    def get_new_corner_buffer(self, avail_moves):
        for new_buffer in self.corner_cycle_break_order:
            if new_buffer in avail_moves:
                return new_buffer

        return random.choice(list(avail_moves))

    # memo
    def memo_corners(self):
        curr = buffer = self.default_corner_buffer
        self.corner_memo_buffers.add(buffer)
        avail_moves = self.corner_swaps
        def_buff_adj = self.adj_corners[buffer]
        curr = avail_moves[curr]
        memo = []
        while avail_moves:
            new_memo = [curr]
            # Memo until a cycle break
            while True:
                curr = avail_moves[curr]
                new_memo.append(curr)
                if curr == buffer or curr in self.adj_corners[buffer]:
                    break

            # Remove memo and adj from avail
            for i in new_memo:
                if i in avail_moves:
                    avail_moves.pop(i)
                    for j in self.adj_corners[i]:
                        avail_moves.pop(j)

            # Remove buffer and adj from avail
            if buffer in avail_moves:
                avail_moves.pop(buffer)
                for i in self.adj_corners[buffer]:
                    avail_moves.pop(i)

            # Append the new memo onto the current memo
            memo += new_memo

            # Return the memo when avail is empty
            if not avail_moves:
                return [
                    m
                    for m in memo
                    if m not in def_buff_adj and m != self.default_corner_buffer
                ]

            # Pick a new corner buffer
            curr = buffer = self.get_new_corner_buffer(avail_moves)
            self.corner_memo_buffers.add(buffer)

    # memo
    def get_new_edge_buffer(self, avail_moves):
        # # TODO: also check the other side of the buffer piece at first
        for new_buffer in self.edge_cycle_break_order:
            if new_buffer in avail_moves:
                return new_buffer

        return random.choice(list(avail_moves))

    # memo
    def memo_edges(self):
        buffer = self.default_edge_buffer
        avail_moves = self.edge_swaps
        def_buff = self.default_edge_buffer
        def_buff_adj = self.adj_edges[self.default_edge_buffer]
        self.edge_memo_buffers.add(buffer)
        curr = avail_moves[buffer]
        memo = []
        while avail_moves:
            new_memo = [curr]
            # Memo until a cycle break
            while True:
                curr = avail_moves[curr]
                new_memo.append(curr)
                if curr == buffer or curr == self.adj_edges[buffer]:
                    break

            # Remove memo and adj from avail
            for move in new_memo:
                if move in avail_moves:
                    avail_moves.pop(move)
                    avail_moves.pop(self.adj_edges.get(move))

            # Remove buffer and adj from avail
            if buffer in avail_moves:
                avail_moves.pop(buffer)
                avail_moves.pop(self.adj_edges.get(buffer))

            # Append the new memo onto the current memo
            memo += new_memo

            # Return the memo when avail is empty
            if not avail_moves:
                return [
                    letter
                    for letter in memo
                    if letter != def_buff and letter != def_buff_adj
                ]

            # Pick a new edge buffer
            curr = buffer = self.get_new_edge_buffer(avail_moves)
            self.edge_memo_buffers.add(buffer)

    @staticmethod
    def format_edge_memo(memo: list[str]):
        return " ".join(f"{memo[i]}{memo[i + 1]}" for i in range(0, len(memo) - 1, 2))

    def format_corner_memo(self, memo) -> str:
        parity_target = memo.pop() if self.has_parity else ""
        memo = self.format_edge_memo(memo) + " " + parity_target
        return memo.strip()

    # memo
    def remove_irrelevant_edge_buffers(self, edges, edge_buffer):
        edges = edges.copy()
        edge_buffer_order = self.edge_buffer_order.copy()
        for buff in edge_buffer_order:
            edges.pop(buff)
            edges.pop(self.adj_edges[buff])

            if set(buff) == set(edge_buffer):
                break
        return edges

    def remove_irrelevant_corner_buffers(self, corners, corner_buffer):

        corner_buffer_order = self.corner_buffer_order.copy()
        for buff in corner_buffer_order:
            corners.pop(buff)
            adj1, adj2 = self.adj_corners[buff]
            corners.pop(adj1)
            corners.pop(adj2)

            if set(buff) == set(corner_buffer):
                break

        return corners


if __name__ == "__main__":
    cube = Cube()
    scram = "R"
    memo_cube = Memo(scram)
