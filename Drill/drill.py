"""Drill session manager for BLD training."""

import itertools
import json
import random
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import dlin
from comms.comms import COMMS
from Commutator.comm_shift import comm_shift
from Cube import Cube
from Cube.memo import Memo
from interface import CLIInterface
from Letterscheme.letterscheme import LetterScheme, convert_letterpairs
from Scramble import get_scramble
from Settings.settings import Settings

DEBUG = 0

_DRILL_CACHE = Path("cache/drill_save.json")
_SCRAMS_DIR = Path("scrams")


def input_with_quit(message: str = "") -> str:
    try:
        response = input(message)
    except KeyboardInterrupt:
        sys.exit()
    else:
        if response.lower().startswith("q"):
            return "return"
        return response


@dataclass
class DrillConfig:
    """Configuration for a buffer drill session."""

    return_list: bool = False
    translate_memo: bool = False
    drill_set: set[str] | None = None
    random_pairs: bool = False
    number_of_scrambles: int = 0


class Drill:
    _MAX_TRIES: ClassVar[int] = 3000
    _LARGE_SET: ClassVar[int] = 60
    _SMALL_SET: ClassVar[int] = 20
    _CYCLE_COUNT_LARGE: ClassVar[int] = 3
    _CYCLE_COUNT_MEDIUM: ClassVar[int] = 2
    _CYCLE_COUNT_SMALL: ClassVar[int] = 1

    def __init__(
        self,
        ui: CLIInterface,
        memo: Memo | None = None,
        buffer_order: list[str] | None = None,
        letter_scheme: LetterScheme | None = None,
        cur_settings: Settings | None = None,
    ) -> None:
        self.ui = ui
        self.cube_memo: Memo = (
            memo if memo is not None else Memo(buffer_order=buffer_order)
        )
        self.letter_scheme: LetterScheme = (
            LetterScheme() if letter_scheme is None else letter_scheme
        )
        self.settings: Settings = (
            Settings(ui=ui) if cur_settings is None else cur_settings
        )
        self.max_cycles_per_buffer: dict[str, int] = {
            "".join(sorted(buffer)): (8 - i) // 2
            for i, buffer in enumerate(self.cube_memo.corner_buffer_order, 1)
        }
        self.max_cycles_per_buffer |= {
            "".join(sorted(buffer)): (12 - i) // 2
            for i, buffer in enumerate(self.cube_memo.edge_buffer_order, 1)
        }
        self.total_cases_per_edge_buffer: list[int] = [
            i * (i - 2) for i in range(22, 2, -2)
        ]
        self.total_cases_per_corner_buffer: list[int] = [
            i * (i - 3) for i in range(21, 3, -3)
        ]
        self.total_cases_per_buffer: dict[str, int] = {
            "".join(sorted(buffer)): num
            for buffer, num in zip(
                self.cube_memo.edge_buffer_order + self.cube_memo.corner_buffer_order,
                self.total_cases_per_edge_buffer + self.total_cases_per_corner_buffer,
                strict=True,
            )
        }

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _compute_cycle_count(self, remaining_count: int) -> int:
        if remaining_count > self._LARGE_SET:
            return self._CYCLE_COUNT_LARGE
        if remaining_count < self._SMALL_SET:
            return self._CYCLE_COUNT_SMALL
        return self._CYCLE_COUNT_MEDIUM

    def _read_drill_cache(self) -> dict:
        with _DRILL_CACHE.open(encoding="utf-8") as f:
            return json.load(f)

    def _write_drill_cache(self, buffer: str, remaining: set[str]) -> None:
        data = self._read_drill_cache()
        data[buffer] = list(remaining)
        with _DRILL_CACHE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _clear_drill_cache(self, buffer: str) -> None:
        data = self._read_drill_cache()
        data[buffer] = []
        with _DRILL_CACHE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _save_scrambles_to_file(self, buffer: str, scrams: dict) -> None:
        timestamp = datetime.now(tz=UTC).strftime("%m-%d-%Y-%H-%M-%S")
        _SCRAMS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = _SCRAMS_DIR / f"buffer-{buffer}-{timestamp}.txt"
        with file_path.open("w", encoding="utf-8") as f:
            for scram, _memo, _comms in scrams.values():
                print(scram, file=f)  # noqa: T201
        self.ui.success(f"Scrambles saved to {file_path}")

    # -------------------------------------------------------------------------
    # Trace
    # -------------------------------------------------------------------------

    def get_dlin_trace(self, scramble: str) -> dict:
        has_parity = (len(scramble.split()) - scramble.count("2")) % 2 == 1
        swap = self.settings.parity_swap_edges.split("-") if has_parity else None

        print(
            "GETTING DLIN TRACE WITH BUFFERS DLIN BUFFERS 3", self.settings.dlin_buffers
        )
        return dlin.trace(scramble, swap=swap, buffers=self.settings.dlin_buffers)

    # -------------------------------------------------------------------------
    # Memo generation
    # -------------------------------------------------------------------------

    # def generate_drill_list(
    #     self,
    #     ltr_scheme: LetterScheme,
    #     buffer: str,
    #     target: str,
    # ) -> set[str]:
    #     all_targets = ltr_scheme.get_corners()
    #     self.remove_piece(all_targets, buffer)
    #     target_list = all_targets[:]
    #     self.remove_piece(target_list, target)
    #     return {target + i for i in target_list}

    # def get_target_scramble(self, algs_to_drill: set[str]) -> tuple[str, str]:
    #     scramble = get_scramble.get_scramble()
    #     cube = Memo(scramble, ls=self.cube_memo.ls)
    #     corner_memo = self.cube_memo.format_corner_memo(cube.memo_corners()).split(" ")
    #     no_cycle_break_corner_memo: set[str] = set()
    #
    #     corner_buffers = cube.corner_memo_buffers
    #     for pair in corner_memo:
    #         if len(pair) in {4, 2}:
    #             half = len(pair) // 2
    #             a, b = pair[:half], pair[half:]
    #         else:
    #             a, b = pair, ""
    #         if a in corner_buffers or b in corner_buffers:
    #             break
    #         no_cycle_break_corner_memo.add(pair)
    #
    #     alg_to_drill = algs_to_drill.intersection(no_cycle_break_corner_memo)
    #     if alg_to_drill:
    #         return scramble, alg_to_drill.pop()
    #     return self.get_target_scramble(algs_to_drill)

    def get_no_cycle_break_memo_corners(
        self,
        scramble: str,
        _letter_scheme: LetterScheme | None,
        buffer: str | None,
        formatted: bool = True,
    ) -> list[str]:
        trace = self.get_dlin_trace(scramble)
        corner_targets: list[str] | None = None
        for cycle in trace["corner"]:
            if cycle["buffer"] == buffer and cycle["targets"]:
                corner_targets = cycle["targets"]
                break

        if not corner_targets:
            return []
        if len(corner_targets) % 2 != 0:
            corner_targets.pop()
        if not corner_targets:
            return []
        if not formatted:
            return corner_targets

        return " ".join(
            f"{corner_targets[i]}{corner_targets[i + 1]}"
            for i in range(0, len(corner_targets) - 1, 2)
        ).split(" ")

    def get_no_cycle_break_memo_edges(
        self,
        scramble: str,
        _letter_scheme: LetterScheme | None,
        buffer: str | None,
        formatted: bool = True,
    ) -> list[str]:
        trace = self.get_dlin_trace(scramble)
        edge_targets: list[str] | None = None
        for cycle in trace["edge"]:
            if cycle["buffer"] == buffer and cycle["targets"]:
                edge_targets = cycle["targets"]
                break

        if not edge_targets:
            return []
        if len(edge_targets) % 2 != 0:
            edge_targets.pop()
        if not edge_targets:
            return []
        if not formatted:
            return edge_targets

        return " ".join(
            f"{edge_targets[i]}{edge_targets[i + 1]}"
            for i in range(0, len(edge_targets) - 1, 2)
        ).split(" ")

    def generate_random_edge_memo(
        self,
        edges: set[str],
        edge_buffer: str | None = None,
        exclude_from_memo: set[str] | None = None,
        random_pairs: bool = False,
    ) -> tuple[str, str]:
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        edge_buffer = (
            self.cube_memo.default_edge_buffer if edge_buffer is None else edge_buffer
        )
        memo: list[str] = []

        edge_list = list(edges) if random_pairs else list(edges - exclude_from_memo)
        random.shuffle(edge_list)

        for pair in edge_list:
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

        scramble = self.cube_memo.scramble_edges_from_memo(memo, str(edge_buffer))
        return scramble, self.cube_memo.format_edge_memo(memo)

    def generate_random_corner_memo(
        self,
        corners: set[str],
        corner_buffer: str | None = None,
        exclude_from_memo: set[str] | None = None,
        random_pairs: bool = False,
    ) -> tuple[str, str]:
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo
        corner_buffer = (
            self.cube_memo.default_corner_buffer
            if corner_buffer is None
            else corner_buffer
        )
        memo: list[str] = []
        memo_set: set[str] = set()

        corners_list = (
            list(corners) if random_pairs else list(corners - exclude_from_memo)
        )
        random.shuffle(corners_list)

        for pair in corners_list:
            corner, corner2 = pair[: len(pair) // 2], pair[len(pair) // 2 :]
            corner_adj1, corner_adj2 = self.cube_memo.adj_corners[corner]
            corner2_adj1, corner2_adj2 = self.cube_memo.adj_corners[corner2]
            if memo_set.intersection(
                {
                    corner,
                    corner_adj1,
                    corner_adj2,
                    corner2,
                    corner2_adj1,
                    corner2_adj2,
                }
            ):
                continue

            memo.extend([corner, corner2])
            memo_set |= {corner, corner2}

            if len(memo) == (
                2 * self.max_cycles_per_buffer["".join(sorted(corner_buffer))]
            ):
                break

        if len(memo) % 2 == 1:
            memo.pop()

        scramble = self.cube_memo.scramble_corners_from_memo(memo, str(corner_buffer))
        return scramble, self.cube_memo.format_corner_memo(memo)

    # -------------------------------------------------------------------------
    # Sticker drills
    # -------------------------------------------------------------------------

    def _run_sticker_drill_loop(
        self,
        algs_to_drill: set[str],
        letter_scheme: LetterScheme | None,
        buffer: str | None,
        get_memo_fn: Callable[[str, LetterScheme | None, str | None], list[str]],
    ) -> None:
        """Shared loop body for corner and edge sticker drills."""
        self.ui.info("Running...")
        number = 0
        tries = 0
        all_algs = algs_to_drill.copy()
        remaining_algs = algs_to_drill.copy()
        len_remaining = len(algs_to_drill)
        cycle_count = self._compute_cycle_count(len(remaining_algs))
        memo_times: list[float] = []
        start = time.perf_counter()

        while remaining_algs:
            scramble = get_scramble.get_scramble_bld()
            memo = get_memo_fn(scramble, letter_scheme, buffer)
            cycles_to_drill = remaining_algs.intersection(set(memo))

            if tries == self._MAX_TRIES or (
                (time.perf_counter() - start) > 2
                and cycle_count > self._CYCLE_COUNT_MEDIUM
            ):
                cycle_count -= 1
                tries = 0

            if len(cycles_to_drill) < cycle_count and tries < self._MAX_TRIES:
                tries += 1
                continue

            if not cycles_to_drill:
                continue

            memo_times.append(time.perf_counter() - start)
            cycle_count = self._compute_cycle_count(len(remaining_algs))
            number += 1
            tries = 0

            self.ui.result("Scramble", f"{number}/{len_remaining}: {scramble}")

            algs_used_ls = list(
                convert_letterpairs(
                    [c for c in memo if c in all_algs],
                    "loc_to_letter",
                    letter_scheme,
                    return_type="list",
                )
            )
            remaining_algs_ls = list(
                convert_letterpairs(
                    remaining_algs,
                    "loc_to_letter",
                    letter_scheme,
                    return_type="list",
                )
            )

            if input_with_quit("Press q to exit:\n") == "return":
                return

            algs_display = ", ".join(
                f"'{a}'" if a not in remaining_algs_ls else a for a in algs_used_ls
            )
            self.ui.result("Algs used", algs_display)

            response = input_with_quit("Enter 'r' to repeat letter pairs: ")
            if response == "return":
                return
            if response == "r":
                len_remaining += len(cycles_to_drill)
                self.ui.blank_line()
                continue

            remaining_algs -= cycles_to_drill
            if len(cycles_to_drill) > 1:
                len_remaining -= len(cycles_to_drill) - 1
            remaining_algs -= remaining_algs.intersection(set(memo))
            self.ui.blank_line()
            start = time.perf_counter()

        if memo_times:
            avg = sum(memo_times) / len(memo_times)
            self.ui.result(
                "Memo",
                f"Avg: {avg:.3f}s, "
                f"Min: {min(memo_times):.3f}s, "
                f"Max: {max(memo_times):.3f}s",
            )

    def drill_corner_sticker(
        self,
        algs_to_drill: set[str],
        letter_scheme: LetterScheme | None = None,
        buffer: str | None = None,
        _random_pairs: bool = False,
        _freq: int = -1,
    ) -> None:
        self._run_sticker_drill_loop(
            algs_to_drill=algs_to_drill,
            letter_scheme=letter_scheme,
            buffer=buffer,
            get_memo_fn=self.get_no_cycle_break_memo_corners,
        )

    def drill_edge_sticker(
        self,
        algs_to_drill: set[str],
        letter_scheme: LetterScheme,
        buffer: str,
        _random_pairs: bool = False,
        _freq: int = -1,
    ) -> None:
        """Brute-force gen-and-check to generate scrambles with a target set of pairs."""
        self._run_sticker_drill_loop(
            algs_to_drill=algs_to_drill,
            letter_scheme=letter_scheme,
            buffer=buffer,
            get_memo_fn=self.get_no_cycle_break_memo_edges,
        )

    def drill_two_color_memo(
        self,
        letter_scheme: LetterScheme | None = None,
        buffer: str | None = None,
    ) -> None:
        self.ui.info("Running...")
        while True:
            scramble = get_scramble.get_scramble()
            no_cb_memo = self.get_no_cycle_break_memo_corners(
                scramble,
                letter_scheme,
                buffer=buffer,
                formatted=False,
            )
            dbr = ("DBR", "BDR", "RDB")
            dfl = ("DFL", "FDL", "LDF")
            dbl = ("DBL", "BDL", "LDB")
            dfr = ("DFR", "FDR", "RDF")

            for i in range(0, len(no_cb_memo) - 1, 2):
                is_dbr_to_dfl = no_cb_memo[i] in dbr and no_cb_memo[i + 1] in dfl
                is_dbl_to_dfr = no_cb_memo[i] in dbl and no_cb_memo[i + 1] in dfr
                if is_dbr_to_dfl or is_dbl_to_dfr:
                    self.ui.info(scramble)
                    if input_with_quit() == "return":
                        return

    # -------------------------------------------------------------------------
    # Cycle-break scramble generation
    # -------------------------------------------------------------------------

    def drill_edge_buffer_cycle_breaks(self, edge_buffer: str) -> str:
        edges = self.cube_memo.remove_irrelevant_edge_buffers(
            self.cube_memo.adj_edges,
            edge_buffer,
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
            cube.scramble_cube(comm_shift(COMMS, edge_buffer, a, b))

        return cube.solve(max_depth=19)

    def drill_corner_buffer_cycle_breaks(self, corner_buffer: str) -> str:
        corners = self.cube_memo.remove_irrelevant_corner_buffers(
            self.cube_memo.adj_corners.copy(),
            corner_buffer,
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
            cube.scramble_cube(comm_shift(COMMS, corner_buffer, a, b))

        return cube.solve(max_depth=19)

    # -------------------------------------------------------------------------
    # Buffer drills
    # -------------------------------------------------------------------------

    def drill_edge_buffer(  # noqa: PLR0912, PLR0915
        self,
        file_comms: dict,
        edge_buffer: str,
        exclude_from_memo: set[str] | None = None,
        config: DrillConfig | None = None,
    ) -> dict:
        cfg = config or DrillConfig()
        scrams: dict = {}
        total_cases = self.total_cases_per_buffer["".join(sorted(edge_buffer))]
        max_count = (
            total_cases // self.max_cycles_per_buffer["".join(sorted(edge_buffer))]
        )
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        edges = self.cube_memo.remove_irrelevant_edge_buffers(
            self.cube_memo.adj_edges,
            edge_buffer,
        )
        all_edges = {
            i + j
            for i, j in itertools.permutations(edges, 2)
            if i != self.cube_memo.adj_edges[j] and i + j not in exclude_from_memo
        }

        if cfg.drill_set is not None:
            exclude_from_memo = all_edges - cfg.drill_set

        num = (
            1
            if cfg.drill_set is None
            else len(exclude_from_memo)
            // self.max_cycles_per_buffer["".join(sorted(edge_buffer))]
            + 1
        )

        while len(exclude_from_memo) < total_cases or cfg.random_pairs:
            scramble, memo = self.generate_random_edge_memo(
                all_edges,
                edge_buffer,
                exclude_from_memo,
                random_pairs=cfg.random_pairs,
            )

            if not cfg.return_list:
                label = (
                    scramble if cfg.random_pairs else f'{num}/{max_count}: "{scramble}"'
                )
                self.ui.result("Scramble", label)

                self._write_drill_cache(edge_buffer, all_edges - exclude_from_memo)

                if input_with_quit() == "return":
                    return scrams

                if cfg.translate_memo:
                    translated = ", ".join(
                        list(
                            convert_letterpairs(
                                memo.split(),
                                direction="loc_to_letter",
                                letter_scheme=self.letter_scheme,
                                piece_type="edges",
                                return_type="list",
                            )
                        )
                    )
                    self.ui.result("Memo", translated)
                else:
                    self.ui.info(memo)

                self.ui.blank_line()

            comms: list = []
            for pair, _pair_letters in zip(
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
                strict=False,
            ):
                exclude_from_memo.add(pair)
                a, b = pair[:2], pair[2:]
                comm = comm_shift(file_comms, edge_buffer, a, b)
                comms.append(comm)

            scrams[num] = [scramble, memo, comms]
            num += 1

            if (
                cfg.return_list
                and cfg.random_pairs
                and num >= cfg.number_of_scrambles + 1
            ):
                break

            if not cfg.return_list:
                self.ui.separator()
                if input_with_quit() == "return":
                    return scrams

        if cfg.return_list:
            self._save_scrambles_to_file(edge_buffer, scrams)

        self.ui.success("Finished")
        self._clear_drill_cache(edge_buffer)
        return scrams

    def drill_corner_buffer(  # noqa: PLR0912, PLR0915
        self,
        corner_buffer: str,
        exclude_from_memo: set[str] | None = None,
        config: DrillConfig | None = None,
        file_comms: dict | None = None,
    ) -> dict:
        cfg = config or DrillConfig()
        scrams: dict = {}
        total_cases = self.total_cases_per_buffer["".join(sorted(corner_buffer))]
        max_count = (
            total_cases // self.max_cycles_per_buffer["".join(sorted(corner_buffer))]
        )
        exclude_from_memo = set() if exclude_from_memo is None else exclude_from_memo

        corners = self.cube_memo.remove_irrelevant_corner_buffers(
            self.cube_memo.adj_corners.copy(),
            corner_buffer,
        )
        all_corners = {
            i + j
            for i, j in itertools.permutations(corners, 2)
            if i != self.cube_memo.adj_corners[j][0]
            and i != self.cube_memo.adj_corners[j][1]
            and i + j not in exclude_from_memo
        }

        if cfg.drill_set is not None:
            exclude_from_memo = all_corners - cfg.drill_set

        num = (
            1
            if cfg.drill_set is None
            else len(exclude_from_memo)
            // self.max_cycles_per_buffer["".join(sorted(corner_buffer))]
            + 1
        )

        while len(exclude_from_memo) < total_cases or cfg.random_pairs:
            scramble, memo = self.generate_random_corner_memo(
                all_corners,
                corner_buffer,
                exclude_from_memo,
                random_pairs=cfg.random_pairs,
            )

            if not cfg.return_list:
                label = (
                    scramble if cfg.random_pairs else f"{num}/{max_count}: {scramble}"
                )
                self.ui.result("Scramble", label)

                self._write_drill_cache(corner_buffer, all_corners - exclude_from_memo)

                if input_with_quit() == "return":
                    return scrams

                translated = ", ".join(
                    list(
                        convert_letterpairs(
                            memo.split(),
                            direction="loc_to_letter",
                            letter_scheme=self.letter_scheme,
                            piece_type="corners",
                        )
                    )
                )
                self.ui.result("Memo", translated)
                self.ui.blank_line()

            comms: list = []
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
                strict=False,
            ):
                exclude_from_memo.add(pair)
                a, b = pair[:3], pair[3:]
                comm = comm_shift(file_comms, corner_buffer, a, b)
                comms.append(comm)
                if not cfg.return_list:
                    self.ui.result(pair_letters, comm if comm else "Not listed")

            scrams[num] = [scramble, memo, comms]
            num += 1

            if (
                cfg.return_list
                and cfg.random_pairs
                and num >= cfg.number_of_scrambles + 1
            ):
                break

            if not cfg.return_list:
                self.ui.separator()
                if input_with_quit() == "return":
                    return scrams

        if cfg.return_list:
            self._save_scrambles_to_file(corner_buffer, scrams)

        self.ui.success("Finished")
        self._clear_drill_cache(corner_buffer)
        return scrams

    # -------------------------------------------------------------------------
    # Misc drill methods
    # -------------------------------------------------------------------------

    def remove_piece(self, target_list: list[str], piece: str) -> list[str]:
        piece_adj1, piece_adj2 = self.cube_memo.adj_corners[piece]
        target_list.remove(piece)
        target_list.remove(piece_adj1)
        target_list.remove(piece_adj2)
        return target_list

    def get_all_buffer_targets(
        self,
        buffer: str,
        piece_type: str = "corners",
    ) -> set[str]:
        if piece_type == "corners":
            corners = self.cube_memo.remove_irrelevant_corner_buffers(
                self.cube_memo.adj_corners.copy(),
                buffer,
            )
            return {
                i + j
                for i, j in itertools.permutations(corners, 2)
                if i != self.cube_memo.adj_corners[j][0]
                and i != self.cube_memo.adj_corners[j][1]
            }
        if piece_type == "edges":
            edges = self.cube_memo.remove_irrelevant_edge_buffers(
                self.cube_memo.adj_edges,
                buffer,
            )
            return {
                i + j
                for i, j in itertools.permutations(edges, 2)
                if i != self.cube_memo.adj_edges[j]
            }
        msg = 'piece_type must be "corners" or "edges"'
        raise ValueError(msg)

    def drill_ltct(self, args: object) -> None:
        self.ui.warning("Currently not available")

    def drill_ltct_scramble(self) -> None:
        while True:
            while True:
                scramble = get_scramble.get_scramble(requires_parity=True)
                self.cube_memo = Memo(scramble)
                twisted_corners = self.cube_memo.twisted_corners
                twisted_corner_count = self.cube_memo.twisted_corners_count
                corner_memo = self.cube_memo.memo_corners()
                if (
                    twisted_corner_count == 1
                    and "U" in corner_memo.pop()
                    and "U" in next(iter(twisted_corners.values()))
                ):
                    break
            print(scramble, end="")  # noqa: T201 — intentional no-newline for input prompt
            if input_with_quit() == "return":
                return

    # -------------------------------------------------------------------------
    # Comm cancellation
    # -------------------------------------------------------------------------

    def parallel_cancel(
        self,
        pre_move: list[str],
        solution: list[str],
    ) -> tuple[list[str], list]:
        sol = solution.copy()
        pre_move_len = len(pre_move)
        solution = pre_move + solution

        if "" in solution:
            solution.remove("")

        opp = {"U": "D", "D": "U", "F": "B", "B": "F", "L": "R", "R": "L"}

        for i in range(len(solution) - 3):
            if DEBUG:
                self.ui.debug(f"SOLUTION {solution}")

            first_turn = solution[i]
            first_layer = first_turn[0]
            second_layer = solution[i + 1][0]
            third_turn = solution[i + 2]
            third_layer = third_turn[0]

            if first_layer == third_layer and first_layer == opp[second_layer]:
                canceled_cube = Cube(first_turn + " " + third_turn)
                kociemba_solution = canceled_cube.solve(invert=True).split()

                if DEBUG:
                    self.ui.debug(f"k sol {kociemba_solution}")

                if i < pre_move_len:
                    pre_move[i] = " ".join(kociemba_solution)
                if i + 2 < pre_move_len:
                    pre_move[i + 2] = ""
                if i >= pre_move_len:
                    sol[i - pre_move_len] = kociemba_solution
                if i + 2 >= pre_move_len:
                    sol[i + 2 - pre_move_len] = ""

                if DEBUG:
                    self.ui.debug(str(pre_move))
                    self.ui.debug(str(solution))

                if "" in pre_move:
                    pre_move.remove("")
                if "" in sol:
                    sol.remove("")

                return self.parallel_cancel(pre_move, sol)

        return pre_move, sol

    def cancel(self, pre_move: str, solution: str) -> str:
        sol_parts = solution.rstrip("\n").strip().split(" ")[:]
        pre_parts = pre_move.rstrip("\n").strip().split(" ")[:]
        pre_parts, sol_parts = self.parallel_cancel(pre_parts, sol_parts)

        rev_pre = pre_parts[::-1]
        if DEBUG:
            self.ui.debug(f"{sol_parts} || {pre_parts} || {rev_pre}")

        solved = Cube()

        for depth, (pre, s) in enumerate(
            zip(rev_pre.copy(), sol_parts.copy(), strict=False)
        ):
            canceled_cube = Cube(pre + " " + s)

            if DEBUG:
                match = solved == canceled_cube
                self.ui.debug(f"{pre} || {s} Full cancel: {'yep' if match else 'nope'}")

            if not pre or not s:
                break

            if DEBUG:
                self.ui.debug(
                    f"{pre} || {s} Partial cancel: {'yep' if pre[0] == s[0] else 'nope'}"
                )

            if solved == canceled_cube and depth < 1:
                rev_pre.remove(pre)
                sol_parts.remove(s)
                if DEBUG:
                    self.ui.debug(f"{sol_parts} || {rev_pre}")
                return self.cancel(" ".join(rev_pre[::-1]), " ".join(sol_parts))

            if pre[0] == s[0] and depth < 1:
                canceled_cube = Cube(pre + " " + s)
                kociemba_solution = canceled_cube.solve(invert=True).split()
                if DEBUG:
                    self.ui.debug(f"k sol {kociemba_solution}")
                    self.ui.debug(str(rev_pre))
                rev_pre.remove(pre)
                sol_parts.remove(s)
                sol_parts = kociemba_solution + sol_parts
                return self.cancel(" ".join(rev_pre[::-1]), " ".join(sol_parts))
            break

        if DEBUG:
            self.ui.debug(
                f"Returning {' '.join(rev_pre[::-1])} || {' '.join(sol_parts)}"
            )
        return " ".join(rev_pre[::-1]) + " " + " ".join(sol_parts).strip()

    # -------------------------------------------------------------------------
    # Twist drills
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_twists() -> dict[str, dict[str, str]]:
        return {
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

    def drill_twists(self, mode: str) -> None:
        """2f: floating 2-twist, 3: 3-twist, or 3f: floating 3-twist."""
        twists = self._get_twists()
        if mode == "3":
            cw = list(itertools.combinations(twists["CW"].values(), r=2))
            ccw = list(itertools.combinations(twists["CCW"].values(), r=2))
            algs = [a + " " + b for a, b in cw + ccw]
        elif mode == "3f":
            cw = list(itertools.combinations(twists["CW"].values(), r=3))
            ccw = list(itertools.combinations(twists["CCW"].values(), r=3))
            algs = [a + " " + b + " " + c for a, b, c in cw + ccw]
        elif mode in {"2f", "2"}:
            cw_twists = list(twists["CW"].values())
            ccw_twists = list(twists["CCW"].values())
            algs = [
                cw + " " + ccw
                for cw, ccw in itertools.product(cw_twists, ccw_twists)
                if not Cube(cw + " " + ccw).is_solved()
            ]
            algs.extend(itertools.chain(cw_twists, ccw_twists))
        else:
            self.ui.warning("Twist pattern not recognized")
            return

        self.drill_algs(algs)

    def drill_algs(self, algs: list[str]) -> None:
        algs_help_num = 0
        algs_help: list[str] = []
        last_solution: str | None = None
        no_repeat = True
        num = 1
        len_algs = len(algs)

        while algs:
            if DEBUG:
                self.ui.debug("getting random alg...")

            # NOTE: was `random.choice(algs.reverse())` — list.reverse() returns
            # None, which is a bug. Fixed to random.choice(algs).
            alg = a = random.choice(algs)
            post_move = self.gen_premove()

            if DEBUG:
                self.ui.debug(str(post_move))

            alg_with_post_move = alg + " " + post_move
            cube = Cube(alg_with_post_move)

            if DEBUG:
                self.ui.debug("kociemba solving...")

            k_sol = cube.solve(max_depth=16)

            if DEBUG:
                self.ui.debug(f"// {post_move} || {k_sol}")
                self.ui.debug(f"SETUP: {post_move} || {alg_with_post_move}")
                self.ui.debug("canceling")

            solution = self.cancel(post_move, k_sol)

            if len(solution.split()) > 25:
                if DEBUG:
                    self.ui.debug(f"Long solution ({len(solution.split())} moves):")
                continue

            if no_repeat:
                algs.remove(alg)

            if DEBUG:
                self.ui.debug("at input...")

            if last_solution != solution:
                self.ui.result(f"Num {num}/{len_algs}", solution)
                num += 1
                last_solution = solution
                response = input_with_quit()
                if response == "return":
                    return
                if response.startswith("a"):
                    self.ui.result("Alg", a)
                    algs_help_num += 1
                    algs_help.append(a)

        self.ui.result("Help used", f"{algs_help_num} — {algs_help}")

    def gen_premove(
        self,
        min_len: int = 1,
        max_len: int = 3,
        requires_parity: bool = False,
    ) -> str:
        if max_len < 1:
            msg = "max_len must be greater than 0"
            raise ValueError(msg)
        if min_len > max_len:
            msg = "min_len cannot be greater than max_len"
            raise ValueError(msg)

        faces = ["U", "L", "F", "R", "B", "D"]
        directions = ["", "'", "2"]
        opp = {"U": "D", "D": "U", "F": "B", "B": "F", "L": "R", "R": "L"}

        scram_len = random.randint(min_len, max_len)
        turn = random.choice(faces)
        scramble = [turn + random.choice(directions)]
        turns = [turn]

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
        if has_parity:
            return joined_scramble
        return self.gen_premove(
            min_len=min_len,
            max_len=max_len,
            requires_parity=requires_parity,
        )

    # -------------------------------------------------------------------------
    # Float / cycle-break drills
    # -------------------------------------------------------------------------

    def cycle_break_float(
        self,
        buffer: str,
        buffer_order: list[str] | None = None,
    ) -> None:
        """Syntax: cbuff <buffer>
        Desc: scrambles with flips/twists and cycle breaks for all buffers
        Aliases: m
        """
        if len(buffer) == 2:  # noqa: PLR2004
            self.cycle_break_floats_edges(buffer, buffer_order=buffer_order)
        else:
            self.cycle_break_floats_corners(buffer, buffer_order=buffer_order)

    def cycle_break_floats_edges(
        self,
        buffer: str,
        buffer_order: list[str] | None = None,
    ) -> None:
        """Syntax: cbuff <edge buffer>
        Desc: scrambles with flips and cycle breaks for all edge buffers
        """
        allow_other_floats = False

        while True:
            drill = Drill(ui=self.ui, buffer_order=buffer_order)
            scram = drill.drill_edge_buffer_cycle_breaks(buffer)
            cube = Cube(scram, can_parity_swap=False)

            if buffer in cube.solved_edges or len(cube.flipped_edges) >= 4:  # noqa: PLR2004
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
                self.ui.info(scram)
                if input_with_quit() == "return":
                    return

    def cycle_break_floats_corners(
        self,
        buffer: str,
        buffer_order: list[str] | None = None,
    ) -> None:
        """Syntax: cbuff <corner buffer>
        Desc: scrambles with twists and cycle breaks for all corner buffers
        """
        allow_other_floats = False

        while True:
            drill = Drill(ui=self.ui, buffer_order=buffer_order)
            scram = drill.drill_corner_buffer_cycle_breaks(buffer)
            cube = Cube(
                scram,
                can_parity_swap=False,
                parity_swap_edges=self.settings.parity_swap_edges,
            )

            if buffer in cube.solved_corners or len(cube.twisted_corners) > 3:  # noqa: PLR2004
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
                self.ui.info(scram)
                if input_with_quit() == "return":
                    return

    def drill_cycle_break_corners(
        self,
        buffer: str,
        sticker_to_drill: str,
    ) -> None:
        while True:
            scramble = get_scramble.get_scramble()
            trace = self.get_dlin_trace(scramble)["corner"]
            buffer_cycle = None
            for corner in trace:
                if corner["buffer"] == buffer:
                    buffer_cycle = corner
                    break

            if buffer_cycle is None:
                continue

            if (
                buffer_cycle["targets"]
                and buffer_cycle["targets"][-1] == sticker_to_drill
                and len(buffer_cycle["targets"]) < 6  # noqa: PLR2004
                and buffer_cycle["parity"] == 1
            ):
                self.ui.info(scramble)
                if input_with_quit("Press q to exit:\n") == "return":
                    return

    def drill_two_flips(self) -> None:
        self.ui.warning("Currently not available")


if __name__ == "__main__":
    ui = CLIInterface()
    drill = Drill(ui=ui)
    ui.info(drill.drill_edge_buffer_cycle_breaks("UB"))
