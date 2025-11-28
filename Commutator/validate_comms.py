import dlin
from Cube import Memo


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

    return False


def validate_comms(comms, buffer, i, name):
    print("=" * 10, f"SHEET {i}:", "BUFFER", buffer, "=" * 10)
    for first_target, sticker_comms in comms[buffer].items():
        for second_target, alg in sticker_comms.items():
            if not alg or not first_target.isalpha() or not second_target.isalpha():
                continue

            if len(buffer) == 3:
                trace = dlin.trace(alg)
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
                trace = dlin.trace(alg)
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

            # what do you mean?!?!?! ['FL', 'BD', 'DL', 'FL'] L' U M U' L' U M' U' L L DB LF LD
            if not check_symmetry(memo, buffer, first_target, second_target):
                print(
                    name,
                    "what do you mean?!?!?!",
                    f"{memo=}",
                    f"{alg=}",
                    f"{buffer}",
                    f"{first_target}",
                    f"{second_target}",
                )
