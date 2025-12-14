from commands.memo import memo
from Settings.settings import BufferOrder, Buffers


def memo_cube(
    scramble,
    settings,
):
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

    scramble = " ".join(scramble)

    if scramble.startswith("-l"):
        _, file_name = scramble.split()
        file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
        with open(file_name) as f:
            for num, scram in enumerate(f.readlines(), 1):
                # print("Scramble number:", num)
                memo(scram.strip("\n").strip().strip('"'), settings)
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

    memo(scramble.strip('"'), settings)
