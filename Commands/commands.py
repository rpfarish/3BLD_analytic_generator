from pathlib import Path
from random import choice, shuffle

from Cube import Memo
from Cube.solution import Solution
from Drill.drill import Drill
from interface import CLIInterface
from Letterscheme.letterscheme import (
    LetterScheme,
    convert_letterpairs,
)
from Settings.settings import Settings


def remove_corner_piece(target_list, piece, letter_scheme):
    """Remove a corner piece and its two adjacent stickers from the target list."""
    piece_adj1, piece_adj2 = Memo(ls=letter_scheme).adj_corners[piece]
    target_list.remove(piece)
    target_list.remove(piece_adj1)
    target_list.remove(piece_adj2)
    return target_list


def remove_edge_piece(target_list, piece, letter_scheme):
    """Remove an edge piece and its adjacent sticker from the target list."""
    piece_adj1 = Memo(ls=letter_scheme).adj_edges[piece]
    target_list.remove(piece)
    target_list.remove(piece_adj1)
    return target_list


def generate_corner_drill_list(ltr_scheme: LetterScheme, buffer, target, invert=False):
    """Generate drill list for corner pieces."""
    all_targets = ltr_scheme.get_corners()
    remove_corner_piece(all_targets, buffer, ltr_scheme)

    target_list = all_targets[:]
    remove_corner_piece(target_list, target, ltr_scheme)

    if invert:
        return {i + target for i in target_list}

    return {target + i for i in target_list}


def generate_edge_drill_list(
    ltr_scheme: LetterScheme, buffer: str, target: str, invert: bool
) -> set[str]:
    """Generate drill list for edge pieces."""
    all_targets = ltr_scheme.get_edges()
    remove_edge_piece(all_targets, buffer, ltr_scheme)

    target_list = all_targets[:]
    remove_edge_piece(target_list, target, ltr_scheme)

    if not invert:
        return {target + i for i in target_list}

    return {i + target for i in target_list}


def select_cycles(
    categorize_cycles: dict[tuple[str, str], list[str]],
    max_cycle_len: int = 3,
) -> list[str]:
    keys = list(categorize_cycles.keys())
    shuffle(keys)  # randomness lives here

    used = set()
    cycles = []
    for a, b in keys:
        if len(cycles) >= max_cycle_len:
            break
        if a not in used and b not in used:
            cycles.append(choice(categorize_cycles[(a, b)]))
            used.add(a)
            used.add(b)

    return cycles


class Commands:
    def __init__(self, ui: CLIInterface, settings: Settings) -> None:
        self.ui = ui
        self.settings = settings

    def memo(self, args) -> None:
        """Memo: memo [scramble] [-l filename] [-s filename]
        Description:
            Describes memorization for a scramble in the given
            letter scheme and provides analysis like approximate
            alg count, dlin trace, or dlin optimal combination
            (Currently only available for edges).
            For scrambles with parity, UF-UR swap is done
            (or whatever swap is specified in settings).
            Swap must preserve F/B edge orientation.
        Options:
            -l filename loads scrambles from FILENAME text file
            -s filename saves SCRAMBLE to FILENAME text file
        Aliases:
            m
        """

        if not args:
            self.ui.warning("No scramble provided")
            self.ui.info("Usage: memo <scramble>")
            self.ui.info("Example: memo R U R' U' R' F R2 U' R' U' R U R' F'")
            return

        scramble = " ".join(args).replace("3'", "")

        if scramble.startswith("-l"):
            _, file_name = scramble.split()
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            with open(file_name) as f:
                for num, scram in enumerate(f.readlines(), 1):
                    # print("Scramble number:", num)

                    if not scram:
                        continue
                    # TODO:: cleanup memo output
                    s = Solution(scram.strip().strip('"'), self.ui, self.settings)
                    s.display()
            return

        elif "-s" in scramble:
            scramble = scramble.strip('"').split()
            f_index = scramble.index("-s")
            file_name = scramble[f_index + 1]
            scramble = scramble[:f_index]
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            scramble = " ".join(scramble)

            with open(file_name, "a+") as f:
                f.write(scramble.strip('"'))
                f.write("\n")
                f.close()

        if not scramble:
            self.ui.warning("No input scramble provided")
            return

        # TODO:: cleanup memo output
        s = Solution(scramble.strip().strip('"'), self.ui, self.settings)
        s.display()

    def drill(self, args):
        """Drill: drill [-c | -e] [-r] [-f]

        Description:
            Drills a list of letterpairs from the text file until all
            pairs are drilled.

            In the text file, enter a pair as AB for just that pair
            or A* to drill all pairs that start with A (or *A for inverses).
            Letterpairs in quotes signify that a pair that was already
            drilled has occurred again.
            If frequency is not specified, it defaults to 3 and
            will reduce as cases decrease.
            Press r to repeat all of the pairs not in quotes.
            Enter q to exit anytime.
        Options:
            -c Loads corner comms to drill from drill_lists/drill_list_corners.txt
            -e Loads edge comms to drill from drill_lists/drill_list_edges.txt
        Not Implemented:
            -r Randomly generates scrambles indefinitely and does not remove drilled letterpairs
            -f Specifies the number of cycles to be included in a scramble (Recommended 2).
        Aliases:
            d
        Usage:
            drill -c
            drill -e -r -f 2
        """

        args = [arg.lower() for arg in args]
        buffers = self.settings.buffers

        freq = -1
        if "-f" in args:
            index = args.index("-f")
            freq = args[index + 1]

        if "-c" in args or "-corner" in args:
            self.drill_corners(args, buffers, freq)
        elif "-e" in args or "-edge" in args:
            self.drill_edges(args, buffers, freq)

    def drill_corners(self, args, buffers, freq):
        letter_scheme = LetterScheme()

        all_corner_letters = {
            i.name for i in letter_scheme.scheme.values() if i.type == "c"
        }
        all_corner_letters.add("*")

        with open("drill_lists/drill_list_corners.txt") as f:
            algs = f.read().splitlines()

        buffer = buffers["corner_buffer"]
        converted_buffer = letter_scheme[buffer]
        piece_adj1, piece_adj2 = Memo(ls=letter_scheme).adj_corners[converted_buffer]

        # calculate the freq of each alg involving a certain piece
        new_algs = set()
        for alg_line in algs:
            alg = alg_line.strip().upper()

            if not alg or alg.startswith("//"):
                continue

            # buffer in list
            if converted_buffer in alg or piece_adj1 in alg or piece_adj2 in alg:
                print(
                    f"Please remove the buffer's letters {converted_buffer}, {piece_adj1} or {piece_adj2} from {alg}"
                )
                print(f"Skipping {alg}")
                continue

            mid = len(alg) // 2
            a, b = alg[:mid], alg[mid:]
            if invalid := [x for x in (a, b) if x not in all_corner_letters]:
                self.ui.warning(f"{alg} has letters {invalid} not in the letterscheme")
                self.ui.info("Skipping...")
                continue

            if "*" in alg:
                starts_with_star = alg.startswith("*")
                sticker_to_drill = alg[starts_with_star]

                algs_to_drill = generate_corner_drill_list(
                    letter_scheme,
                    converted_buffer,
                    sticker_to_drill,
                    invert=starts_with_star,
                )

                sticker_algs = convert_letterpairs(
                    algs_to_drill,
                    "letter_to_loc",
                    letter_scheme,
                    piece_type="corners",
                )
                new_algs.update(sticker_algs)
                continue

            converted = letter_scheme.convert_pair_to_pos_type(alg, "corner")
            new_algs.add("".join(converted))

        algs = new_algs
        if not algs:
            print("Algs to drill is empty")
            return

        # categorize_cycles: dict[tuple[str, str], list[str]] = defaultdict(list)
        # # get split pair
        # # rotate name to buffer name
        # # sort pair to buffer order
        #
        # buffer_weight = {buffer: i for i, buffer in enumerate(DEFAULTBUFFERS["corner"])}
        # for pair in algs:
        #     a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
        #     ra, rb = rotate_face_precedence(a), rotate_face_precedence(b)
        #     x, y = sorted([ra, rb], key=lambda x: buffer_weight[x])
        #     categorize_cycles[(x, y)].append(a + b)
        #
        # # pprint(categorize_cycles)
        #
        # # how to choose non overlap pairs?
        #
        # cycles = select_cycles(categorize_cycles)
        # print("cycles", cycles)

        Drill(self.ui).drill_corner_sticker(
            algs_to_drill=algs,
            letter_scheme=LetterScheme(),
            buffer=buffers["corner_buffer"],
            _random_pairs="-r" in args,
            _freq=freq,
        )

    def drill_edges(self, args, buffers, freq):
        letter_scheme = LetterScheme()

        all_edge_letters = {
            i.name for i in letter_scheme.scheme.values() if i.type == "e"
        }
        all_edge_letters.add("*")

        with Path("drill_lists/drill_list_edges.txt").open() as f:
            algs = f.read().splitlines()

        buffer = buffers["edge_buffer"]
        converted_buffer = letter_scheme[buffer]
        piece_adj1 = Memo(ls=letter_scheme).adj_edges[converted_buffer]

        # calculate the freq of each alg involving a certain piece
        new_algs = set()
        for alg_line in algs:
            alg = alg_line.strip().upper()

            if not alg or alg.startswith("//"):
                continue

            if converted_buffer in alg or piece_adj1 in alg:
                print(
                    f"Please remove the buffer's letters {converted_buffer}, {piece_adj1} "
                )

                self.ui.info(f"Skipping {alg}")
                continue

            mid = len(alg) // 2
            a, b = alg[:mid], alg[mid:]
            if invalid := [x for x in (a, b) if x not in all_edge_letters]:
                self.ui.warning(f"{alg} has letters {invalid} not in the letterscheme")
                self.ui.info("Skipping...")
                continue

            if "*" in alg:
                starts_with_star = alg.startswith("*")
                sticker_to_drill = alg[starts_with_star]

                algs_to_drill = generate_edge_drill_list(
                    letter_scheme,
                    converted_buffer,
                    sticker_to_drill,
                    invert=starts_with_star,
                )

                sticker_algs = convert_letterpairs(
                    algs_to_drill,
                    "letter_to_loc",
                    letter_scheme,
                    piece_type="edges",
                )
                new_algs.update(sticker_algs)
                continue

            converted = letter_scheme.convert_pair_to_pos_type(alg, "edge")
            new_algs.add("".join(converted))

        algs = new_algs
        if not algs:
            print("Algs to drill is empty")
            return

        # categorize_cycles: dict[tuple[str, str], list[str]] = defaultdict(list)
        # # get split pair
        # # rotate name to buffer name
        # # sort pair to buffer order
        # buffer_weight = {buf: i for i, buf in enumerate(DEFAULTBUFFERS["edge"])}
        #
        # for pair in algs:
        #     a, b = pair[: len(pair) // 2], pair[len(pair) // 2 :]
        #     ra, rb = rotate_face_precedence(a), rotate_face_precedence(b)
        #     x, y = sorted([ra, rb], key=lambda x: buffer_weight[x])
        #     categorize_cycles[(x, y)].append(a + b)
        #
        # # pprint(categorize_cycles)
        #
        # # how to choose non overlap pairs?
        #
        # cycles = select_cycles(categorize_cycles, 5)
        # print("cycles", cycles)
        #
        # print(algs)

        Drill(self.ui).drill_edge_sticker(
            algs_to_drill=algs,
            letter_scheme=LetterScheme(),
            buffer=buffers["edge_buffer"],
            _random_pairs="-r" in args,
            _freq=freq,
        )
