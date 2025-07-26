from Cube.letterscheme import LetterScheme


def get_comm(args, file_comms, eli_comms, comm_file_names, letterscheme: LetterScheme):
    # capitalization is good
    buffer, *cycles = args
    buffer = buffer.upper()

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = LetterScheme().convert_pair_to_pos(buffer, cycle)
        if letterscheme.is_default:
            let1, let2 = a, b
        else:
            let1, let2 = cycle
            # print(
            #     f"Eli {let1 + let2}:",
            #     eli_comms.get(buffer, {}).get(a, {}).get(b, "Not listed"),
            # )
            for comm_file_name, comms in zip(comm_file_names, file_comms):
                list_name_underscore, *_ = comm_file_name.split("_")
                list_name_space, *_ = comm_file_name.split()
                list_name = (
                    list_name_underscore
                    if len(list_name_underscore) < len(list_name_space)
                    else list_name_space
                )

                print(
                    f"{list_name.title()} {let1 + let2}:",
                    comms.get(buffer, {}).get(a, {}).get(b, "Not listed"),
                )
        # I think I should create an object for lists and just pass that then
        # I wouldn't have to
        # should it show just the expanded ver or the comm notation?
        # todo like save both a normal comm version and an expanded version
    return buffer
