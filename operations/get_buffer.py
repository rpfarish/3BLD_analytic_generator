from Cube.letterscheme import LetterScheme


def get_comm(args, file_comms, eli_comms, file_name, letterscheme: LetterScheme):
    # capitalization is good
    file_list = True
    eli_list = True
    file_first_letter = file_name[0]
    list_name, _ = file_name.split("_")
    # if '-b' not in args:
    if '-e' in args:
        args.remove('-e')
        eli_list = True
        file_list = False

    elif f'-{file_first_letter}' in args:
        args.remove(f'-{file_first_letter}')
        eli_list = False
        file_list = True

    buffer, *cycles = args
    buffer = buffer.upper()

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    # iterate the cycles
    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = LetterScheme().convert_pair_to_pos(buffer, cycle)
        if letterscheme.is_default:
            let1, let2 = a, b
        else:
            let1, let2 = cycle
        if file_list:
            print(f"{list_name.title()} {let1 + let2}:", file_comms.get(buffer, {}).get(a, {}).get(b, "Not listed"))
        if eli_list:
            print(f"Eli {let1 + let2}:", eli_comms.get(buffer, {}).get(a, {}).get(b, "Not listed"))

        # should it show just the expanded ver or the comm notation?
    return buffer
