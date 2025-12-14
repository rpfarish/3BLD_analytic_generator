from Commutator.comm_shift import _get_comm, comm_shift
from Commutator.invert_solution import invert_solution
from Cube.letterscheme import LetterScheme, sort_face_precedence


def get_comm(args, file_comms, letterscheme: LetterScheme):
    # capitalization is good
    buffer, *cycles = args
    buffer = buffer.upper()
    buffer = sort_face_precedence(buffer)

    # Name person, comm name: comm notation, expanded comm?
    # prob comm lists should be json lol

    max_len = max(len(name) for name, _ in file_comms)

    for cycle in cycles:
        # do I check both? prob just the first one haha
        cycle = cycle.upper()
        a, b = LetterScheme().convert_pair_to_pos(buffer, cycle)
        if letterscheme.is_default:
            let1, let2 = a, b
        else:
            let1, let2 = cycle

        for list_name, comms in file_comms:
            cur_comm = _get_comm(comms, buffer, a, b)
            if not cur_comm:
                cur_comm = comm_shift(comms, buffer, a, b)

            if not cur_comm:
                cur_comm = invert_solution(_get_comm(comms, buffer, b, a))
            if not cur_comm:
                cur_comm = invert_solution(comm_shift(comms, buffer, b, a))

            result = cur_comm if cur_comm else "Not listed!"
            print(f"{list_name.title():<{max_len}} {let1 + let2}: {result}")

        # I think I should create an object for lists and just pass that then
        # I wouldn't have to
        # should it show just the expanded ver or the comm notation?
        # TODO::: like save both a normal comm version and an expanded version
    return buffer
