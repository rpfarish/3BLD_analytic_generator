from Cube import Memo


def validate_comms(comms, buffer, i):
    print("=" * 10, "INDEX", i, "=" * 10)
    for first_target, sticker_comms in comms[buffer].items():
        for second_target, alg in sticker_comms.items():
            if not alg or not first_target.isalpha() or not second_target.isalpha():
                continue
            # print(first_target, second_target, alg)
            if len(buffer) == 3:
                memo = Memo(alg).memo_corners()
            elif len(buffer) == 2:
                memo = Memo(alg).memo_edges()
            else:
                raise ValueError("Buffer incorrect len")

            if buffer == "UFR" and first_target == "RDF" and second_target == "DBR":

                pass
                # print(
                #     "YES HERE IT IS:",
                #     first_target,
                #     second_target,
                #     alg,
                # )
                #
                # print(memo == [second_target, first_target])
                # print(memo)

            # print(buffer, memo)
            if not (
                memo == [buffer, second_target, first_target, buffer]
                or memo == [second_target, first_target]
                or memo == [second_target, first_target, buffer, second_target]
            ):
                print(
                    "what do you mean?!?!?!",
                    memo,
                    alg,
                    buffer,
                    first_target,
                    second_target,
                )
