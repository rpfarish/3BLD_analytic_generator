from collections import deque

import dlin


def compare_strings(correct: str, wrong: str) -> tuple[str, str]:
    correct_output = ""
    wrong_output = ""

    for c, w in zip(correct, wrong):
        correct_output += c if c == w else f"\033[92m{c}\033[0m"
        wrong_output += w if c == w else f"\033[91m{w}\033[0m"

    return correct_output, wrong_output


def check_corner_symmetry(memo, buffer, x, y) -> bool:

    corner_ori = {
        "DFL": ["LDF", "FDL", "DFL"],
        "DFR": ["RDF", "DFR", "FDR"],
        "FLU": ["LUF", "UFL", "FUL"],
        "FRU": ["RUF", "FUR", "UFR"],
        "BDL": ["LDB", "DBL", "BDL"],
        "BDR": ["RDB", "BDR", "DBR"],
        "BLU": ["LUB", "BUL", "UBL"],
        "BRU": ["RUB", "UBR", "BUR"],
    }

    i, j, k = "".join(sorted(buffer)), "".join(sorted(x)), "".join(sorted(y))

    index1, index2, index3 = (
        corner_ori[i].index(buffer),
        corner_ori[j].index(x),
        corner_ori[k].index(y),
    )

    for index in range(3):
        q = deque(
            [
                corner_ori[i][(index1 + index) % 3],
                corner_ori[j][(index2 + index) % 3],
                corner_ori[k][(index3 + index) % 3],
            ]
        )
        for _ in range(3):
            q.rotate(1)
            if [*q] == memo:
                return True

    return False


def check_symmetry(memo, buffer, first_target, second_target) -> bool:
    if (
        memo == [buffer, second_target, first_target]
        or memo == [second_target, first_target, buffer]
        or memo == [first_target, buffer, second_target]
    ):
        return True

    if len(buffer) == 2:
        buffer = buffer[::-1]
        first_target = first_target[::-1]
        second_target = second_target[::-1]

        if (
            memo == [buffer, second_target, first_target]
            or memo == [second_target, first_target, buffer]
            or memo == [first_target, buffer, second_target]
        ):
            return True
    elif len(buffer) == 3:
        return check_corner_symmetry(memo, buffer, first_target, second_target)

    return False


def validate_comms(comms, buffer, i, name, corner_buffers, edge_buffers):
    print("=" * 10, f"SHEET {i}:", "BUFFER", buffer, "=" * 10)
    buffers = dlin.DEFAULTBUFFERS.copy()
    if len(corner_buffers) + len(edge_buffers) == 16:
        if sorted(corner_buffers[-1]) == sorted(buffers["corner"][-2]):
            buffers["corner"][-2], buffers["corner"][-3] = (
                buffers["corner"][-3],
                buffers["corner"][-2],
            )
        buffers["edge"][: len(edge_buffers)] = edge_buffers
        buffers["corner"][: len(corner_buffers)] = corner_buffers

    for first_target, sticker_comms in comms[buffer].items():
        for second_target, alg in sticker_comms.items():
            if not alg or not first_target.isalpha() or not second_target.isalpha():
                continue

            trace = dlin.trace(alg, buffers=buffers)
            if len(buffer) == 3:
                if trace["edge"]:
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("corner alg does not preserve edges")
                if len(trace["corner"]) > 1:
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("corner alg does not cycle only 3 corners")

                cur_corner = trace["corner"].pop()
                if (
                    cur_corner["type"] != "cycle"
                    or len(cur_corner["targets"]) != 2
                    or cur_corner["orientation"] != 0
                    or cur_corner["parity"] != 0
                ):
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("comm does an invalid cycle")
                    continue

                memo = [cur_corner["buffer"], *cur_corner["targets"]]

            elif len(buffer) == 2:
                if trace["corner"]:
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("edge alg does not preserve corners")
                if len(trace["edge"]) > 1:
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("edge alg does not cycle only 3 edges")
                cur_edge = trace["edge"].pop()
                if (
                    cur_edge["type"] != "cycle"
                    or len(cur_edge["targets"]) != 2
                    or cur_edge["orientation"] != 0
                    or cur_edge["parity"] != 0
                ):
                    print(
                        f"{alg=}",
                        f"{buffer}",
                        f"{first_target}",
                        f"{second_target}",
                    )
                    print("comm does an invalid cycle")
                    continue
                memo = [cur_edge["buffer"], *cur_edge["targets"]]

            else:
                raise ValueError("Buffer incorrect len")

            if not check_symmetry(memo, buffer, first_target, second_target):
                case = f"{buffer} {first_target} {second_target}"
                b, *pair = memo
                pair[::-1] = pair
                memo = b, *pair
                memo = " ".join(memo)
                is_inverse = pair == [first_target, second_target]
                correct, output = compare_strings(case, memo)
                error_msg = f"Sheet: {name}, Case: '{correct}' does {'inverse ' * is_inverse}'{output}' with alg: {alg}"
                print(error_msg)
    print()
