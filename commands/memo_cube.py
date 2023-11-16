from commands.memo import memo


def memo_cube(scramble, letter_scheme, buffers, parity_swap_edges, buffer_order):
    """Memo: memo [scramble] [-l filename] [-s filename]
Options:
    -l filename loads scrambles from FILENAME text file
    -s filename saves SCRAMBLE to FILENAME text file
Aliases:
    m
    """

    scramble = " ".join(scramble)

    if scramble.startswith('-l'):
        _, file_name = scramble.split()
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        with open(file_name) as f:
            for num, scram in enumerate(f.readlines(), 1):
                # print("Scramble number:", num)
                memo(scram.strip("\n").strip().strip('"'), letter_scheme, buffers, parity_swap_edges, buffer_order)
        return

    elif '-s' in scramble:
        scramble = scramble.strip('"').split()
        f_index = scramble.index('-s')
        file_name = scramble[f_index + 1]
        scramble = scramble[:f_index]
        file_name = f"{file_name}.txt" if '.txt' not in file_name else file_name
        scramble = " ".join(scramble)

        with open(file_name, 'a+') as f:
            f.write(scramble.strip('"'))
            f.write("\n")
            f.close()

    memo(scramble.strip('"'), letter_scheme, buffers, parity_swap_edges, buffer_order=buffer_order)
